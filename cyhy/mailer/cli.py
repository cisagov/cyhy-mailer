#!/usr/bin/env python3

"""cyhy-mailer: A tool for mailing out Cyber Hygiene, trustymail, and https-scan reports.

Usage:
  cyhy-mailer report [--cyhy-report-dir=DIRECTORY] [--tmail-report-dir=DIRECTORY] [--https-report-dir=DIRECTORY] [--cybex-scorecard-dir=DIRECTORY] [--mail-server=SERVER] [--mail-port=PORT] [--db-creds-file=FILENAME] [--batch-size=SIZE] [--summary-to=EMAILS] [--debug]
  cyhy-mailer adhoc --subject=SUBJECT --html-body=FILENAME --text-body=FILENAME [--to=EMAILS] [--cyhy] [--cyhy-federal] [--mail-server=SERVER] [--mail-port=PORT] [--db-creds-file=FILENAME] [--batch-size=SIZE] [--summary-to=EMAILS] [--debug]
  cyhy-mailer (-h | --help)

Options:
  -h --help                    Show this message.
  --cyhy-report-dir=DIRECTORY  The directory where the Cyber Hygiene
                               PDF reports are located.  If not
                               specified then no Cyber Hygiene reports
                               will be sent.
  --tmail-report-dir=DIRECTORY The directory where the trustymail PDF reports
                               are located.  If not specified then no trustymail
                               reports will be sent.
  --https-report-dir=DIRECTORY The directory where the https-scan PDF reports
                               are located.  If not specified then no https-scan
                               reports will be sent.
  --cybex-scorecard-dir=DIRECTORY The directory where the Cybex PDF
                               scorecard is located.  If not specified
                               then no Cybex scorecard will be sent.
  -m --mail-server=SERVER      The hostname or IP address of the mail server
                               that should send the messages.
                               [default: smtp01.ncats.cyber.dhs.gov]
  -p --mail-port=PORT          The port to use when connecting to the mail
                               server that should send the messages.
                               [default: 25]
  -c --db-creds-file=FILENAME  A YAML file containing the Cyber
                               Hygiene database credentials.
                               [default: /run/secrets/database_creds.yml]
  --batch-size=SIZE            The batch size to use when retrieving results
                               from the Mongo database.  If not present then
                               the default Mongo batch size will be used.
  --summary-to=EMAILS          A comma-separated list of email addresses to
                               which the summary statistics should be sent at
                               the end of the run.  If not specified then no
                               summary will be sent.
  -d --debug                   A Boolean value indicating whether the output
                               should include debugging messages or not.
  --subject=SUBJECT            The subject line when sending an ad hoc
                               email message.
  --html-body=FILENAME         The file containing the HTML body text
                               when sending an ad hoc email message.
  --text-body=FILENAME         The file containing the text body text
                               when sending an ad hoc email message.
  --to=EMAILS                  A comma-separated list of additional
                               email addresses to which the ad hoc
                               message should be sent.
  --cyhy                       If present, then the ad hoc message
                               will be sent to all Cyber Hygiene
                               agencies.
  --cyhy-federal               If present, then the ad hoc message
                               will be sent to all Federal Cyber
                               Hygiene agencys.  (Note that --cyhy
                               implies --cyhy-federal.)
"""

import datetime
import docopt
import glob
import logging
import re
import smtplib
from socket import timeout

from pymongo import MongoClient
import pymongo.errors
import yaml

from cyhy.mailer import __version__
from cyhy.mailer.CybexMessage import CybexMessage
from cyhy.mailer.CyhyMessage import CyhyMessage
from cyhy.mailer.HttpsMessage import HttpsMessage
from cyhy.mailer.Message import Message
from cyhy.mailer.ReportMessage import ReportMessage
from cyhy.mailer.StatsMessage import StatsMessage
from cyhy.mailer.TmailMessage import TmailMessage


def database_from_config_file(config_filename):
    """Given the name of the YAML file containing the configuration
    information, return a corresponding MongoDB connection.

    The configuration file should something look like this:
        version: '1'

        database:
          name: cyhy
          uri: mongodb://<read-only user>:<password>@<hostname>:<port>/cyhy

    Parameters
    ----------
    config_filename : str
        The name of the YAML file containing the configuration
        information

    Returns
    -------
    MongoDatabase: A connection to the desired MongoDB database

    Throws
    ------
    OSError: If the database configuration file does not exist

    yaml.YAMLError: If the YAML in the database configuration file is
    invalid

    KeyError: If the YAML in the database configuration file is valid
    YAML but does not contain the expected keys

    pymongo.errors.ConnectionError: If unable to connect to the
    requested server

    pymongo.errors.InvalidName: If the requested database does not
    exist
    """
    with open(config_filename, 'r') as stream:
        config = yaml.load(stream)

    db_uri = config['database']['uri']
    db_name = config['database']['name']

    db_connection = MongoClient(host=db_uri, tz_aware=True)
    return db_connection[db_name]


def get_emails_from_request(request):
    """Given the request document, return the proper email address or
    addresses to use for corresponding with the agency.

    Parameters
    ----------
    request : dict
        The request documents for which the corresponding email
        address is desired.

    Returns
    -------
    list of str: A list containing the proper email addresses to use
    for corresponding with the agency
    """
    id = request['_id']
    # Drop any contacts that do not have both a type and a non-empty email
    # attribute...
    contacts = [c for c in request['agency']['contacts'] if 'type' in c and 'email' in c and c['email'].split()]
    # ...but let's log a warning about them.
    for c in request['agency']['contacts']:
        if 'type' not in c or 'email' not in c or not c['email'].split():
            logging.warn('Agency with ID {} has a contact that is missing an email and/or type attribute!'.format(id))

    distro_emails = [c['email'] for c in contacts if c['type'] == 'DISTRO']
    technical_emails = [c['email'] for c in contacts if c['type'] == 'TECHNICAL']

    # There should be zero or one distro email, so log a warning if
    # there are multiple.
    if len(distro_emails) > 1:
        logging.warn('More than one DISTRO email address for agency with ID {}'.format(id))

    # Send to the distro email, if it exists.  Otherwise, send to the
    # technical emails.
    to_emails = distro_emails
    if not to_emails:
        to_emails = technical_emails

    # At this point to_emails should contain at least one email
    if not to_emails:
        logging.error('No emails found for ID {}'.format(id))

    return to_emails


def get_all_descendants(db, parent):
    """Return all (non-retired) descendents of the given Cyber Hygiene
    parent

    Parameters
    ----------
    db : MongoDatabase
        The Mongo database from which Cyber Hygiene agency data can
        be retrieved.

    parent : str
        The Cyber Hygiene parent for which all descendents are desired.

    Returns
    -------
    list of str: The descendents of the Cyber Hygiene parent.
    """
    current_request = db.requests.find_one({'_id': parent})
    if not current_request:
        raise ValueError(parent + ' has no request document')

    descendants = []
    if current_request.get('children'):
        for child in current_request['children']:
            if not db.requests.find_one({'_id': child}).get('retired'):
                descendants.append(child)
                descendants += get_all_descendants(db, child)

    return descendants


def get_cyhy_requests(db, batch_size):
    """Return a cursor that can be used to iterate over the Cyber Hygiene
    agencies.

    Parameters
    ----------
    db : MongoDatabase
        The Mongo database from which Cyber Hygiene agency data can be
        retrieved.

    batch_size : int
        The batch size to use when retrieving results from the Mongo
        database.  If None then the default will be used.

    Returns
    -------
    pymongo.cursor.Cursor: A cursor that can be used to iterate over
    the Cyber Hygiene agencies.

    Throws
    ------
    TypeError: If unable to connect to the requested server, or if
    batch_size is not an int or None.

    ValueError: If batch_size is negative.

    pymongo.errors.InvalidOperation: If the cursor has already been
    used.  The batch size cannot be set on a cursor that has already
    been used.
    """
    try:
        requests = db.requests.find({'retired': {'$ne': True}, 'report_types': 'CYHY'}, {'_id': True, 'agency.acronym': True, 'agency.contacts.email': True, 'agency.contacts.type': True})
        if batch_size is not None:
            requests.batch_size(batch_size)
    except (TypeError, ValueError, pymongo.errors.InvalidOperation):
        logging.critical('There was an error with the MongoDB query that retrieves the list of agencies', exc_info=True)
        raise

    return requests


def get_federal_cyhy_requests(db):
    """Return a cursor that can be used to iterate over the Federal Cyber
    Hygiene agencies.

    Parameters
    ----------
    db : MongoDatabase
        The Mongo database from which Federal Cyber Hygiene agency
        data can be retrieved.

    Returns
    -------
    pymongo.cursor.Cursor: A cursor that can be used to iterate over
    the Federal Cyber Hygiene agencies.

    Throws
    ------
    pymongo.errors.TypeError: If unable to connect to the requested
    server

    """
    fed_orgs = get_all_descendants(db, 'FEDERAL')
    try:
        requests = db.requests.find({'retired': {'$ne': True}, 'report_types': 'CYHY', '_id': {'$in': fed_orgs}}, {'_id': True, 'agency.acronym': True, 'agency.contacts.email': True, 'agency.contacts.type': True})
    except TypeError:
        logging.critical('There was an error with the MongoDB query that retrieves the list of agencies', exc_info=True)
        raise

    return requests


def send_message(mail_server, message, counter=None):
    """Send a message.

    Parameters
    ----------
    mail_server : smtplib.SMTP
        The mail server via which the message is to be sent.

    message : email.message.Message
        The email message that is to be sent.

    counter : int
        A counter.

    Returns
    -------
    int: If counter was not None, then counter + 1 is returned if the
    message was sent sent successfully and counter is returned if not.
    If counter was None then None is returned.

    Throws
    ------
    smtplib.SMTPRecipientsRefused: If all recipients are refused.

    smtplib.SMTPHelpError: If the server did not reply properly to the
    HELO greeting.

    smtplib.SMTPSenderRefused: If the server did not accept the from
    address.

    smtp.SMTPDataError: If the server replied with an unexpected error
    code.

    smtp.SMTPNotSupportedError: If SMTP is not supported by the server.

    """
    # "Are you silly?  I'm still gonna send it!"
    #   -- Larry Enticer
    try:
        mail_server.send_message(message)
        if counter is not None:
            counter += 1
    except (smtplib.SMTPRecipientsRefused, smtplib.SMTPHeloError, smtplib.SMTPSenderRefused, smtplib.SMTPDataError, smtplib.SMTPNotSupportedError):
        # See
        # https://docs.python.org/3/library/smtplib.html#smtplib.SMTP.sendmail
        # for a full list of the exceptions that smtplib.SMTP.send_message can
        # throw.
        logging.error('Unable to send message', exc_info=True, stack_info=True)
        raise

    return counter


def do_report(db, batch_size, mail_server, cyhy_report_dir, tmail_report_dir, https_report_dir, cybex_scorecard_dir, summary_to):
    """Given the parameters, send out Cyber Hygiene, Trustworthy
    Email, HTTPS reports, and a summary email out as appropriate.

    Parameters
    ----------
    db : MongoDatabase
        The Mongo database from which Cyber Hygiene agency data can
        be retrieved.

    batch_size : int
        The batch size to use when retrieving results from the Mongo
        database.  If None then the default will be used.

    mail_server : smtplib.SMTP
        The mail server via which outgoing mail should be sent.

    cyhy_report_dir : str
        The directory where the Cyber Hygiene reports can be found.
        If None then no Cyber Hygiene reports will be sent.

    tmail_report_dir : str
        The directory where the Trustworthy Email reports can be
        found.  If None then no Trustworthy Email reports will be
        sent.

    https_report_dir : str
        The directory where the HTTPS reports can be found.  If None
        then no HTTPS reports will be sent.

    cybex_scorecard_dir : str
        The directory where the Cybex scorecard can be found.  If None
        then no Cybex scorecard will be sent.

    summary_to : str
        A comma-separated list of email addresses to which the
        summary statistics should be sent at the end of the run.  If
        None then no summary will be sent.
    """
    try:
        requests = get_cyhy_requests(db, batch_size)
    except TypeError:
        return 4

    try:
        total_agencies = requests.count()
        logging.debug('Total agencies = {}'.format(total_agencies))
    except pymongo.errors.OperationFailure:
        logging.critical('Mongo database error while counting the number of request documents returned', exc_info=True)
    agencies_emailed_cyhy_reports = 0
    agencies_emailed_tmail_reports = 0
    agencies_emailed_https_reports = 0
    cybex_report_emailed = False
    for request in requests:
        id = request['_id']
        acronym = request['agency']['acronym']

        to_emails = get_emails_from_request(request)
        # to_emails should contain at least one email
        if not to_emails:
            continue

        ###
        # Find and mail the CyHy report, if necessary
        ###
        if cyhy_report_dir:
            # The '2' is necessary because in some cases we have both XYZ and
            # XYZ-AB as stakeholders.  Without the '2' the glob would include
            # both for the ID XYZ.
            cyhy_report_glob = '{}/cyhy-{}-2*.pdf'.format(cyhy_report_dir, id)
            cyhy_report_filenames = sorted(glob.glob(cyhy_report_glob))

            # Exactly one CyHy report should match
            if len(cyhy_report_filenames) > 1:
                logging.warn('More than one Cyber Hygiene report found for agency with ID {}'.format(id))
            elif not cyhy_report_filenames:
                # This is an error since we are starting from the list
                # of CyHy agencys and they should all have reports
                logging.error('No Cyber Hygiene report found for agency with ID {}'.format(id))

            if cyhy_report_filenames:
                # We take the last filename since, if there happens to be more
                # than one, it should the latest.  (This is because we sorted
                # the glob results.)
                cyhy_attachment_filename = cyhy_report_filenames[-1]

                # Extract the report date from the report filename
                match = re.search(r'-(?P<date>\d{4}-[01]\d-[0-3]\d)T', cyhy_attachment_filename)
                report_date = datetime.datetime.strptime(match.group('date'), '%Y-%m-%d').strftime('%B %d, %Y')

                # Construct the CyHy message to send
                message = CyhyMessage(to_emails, cyhy_attachment_filename, acronym, report_date)

                try:
                    agencies_emailed_cyhy_reports = send_message(mail_server, message, agencies_emailed_cyhy_reports)
                except (smtplib.SMTPRecipientsRefused, smtplib.SMTPHeloError, smtplib.SMTPSenderRefused, smtplib.SMTPDataError, smtplib.SMTPNotSupportedError):
                    logging.error('Unable to send Cyber Hygiene report for agency with ID {}'.format(id), exc_info=True, stack_info=True)

        ###
        # Find and mail the trustymail report, if necessary
        #
        # This is very similar to the CyHy block but slightly
        # different.  I need to figure out how to isolate the common
        # functionality into a class or functions.
        ###
        if tmail_report_dir:
            # The '2' is necessary because in some cases we have both XYZ and
            # XYZ-AB as stakeholders.  Without the '2' the glob would include
            # both for the ID XYZ.
            tmail_report_glob = '{}/cyhy-{}-2*.pdf'.format(tmail_report_dir, id)
            tmail_report_filenames = sorted(glob.glob(tmail_report_glob))

            # At most one Tmail report should match
            if len(tmail_report_filenames) > 1:
                logging.warn('More than one Trustworthy Email report found for agency with ID {}'.format(id))
            elif not tmail_report_filenames:
                # This is only at info since we are starting from the
                # list of CyHy agencys.  Many of them will not have
                # Tmail reports.
                logging.info('No Trustworthy Email report found for agency with ID {}'.format(id))

            if tmail_report_filenames:
                # We take the last filename since, if there happens to be more
                # than one, it should the latest.  (This is because we sorted
                # the glob results.)
                tmail_attachment_filename = tmail_report_filenames[-1]

                # Extract the report date from the report filename
                match = re.search(r'-(?P<date>\d{4}-[01]\d-[0-3]\d)-tmail-report', tmail_attachment_filename)
                report_date = datetime.datetime.strptime(match.group('date'), '%Y-%m-%d').strftime('%B %d, %Y')

                # Construct the Tmail message to send
                message = TmailMessage(to_emails, tmail_attachment_filename, acronym, report_date)

                try:
                    agencies_emailed_tmail_reports = send_message(mail_server, message, agencies_emailed_tmail_reports)
                except (smtplib.SMTPRecipientsRefused, smtplib.SMTPHeloError, smtplib.SMTPSenderRefused, smtplib.SMTPDataError, smtplib.SMTPNotSupportedError):
                    logging.error('Unable to send Trustworthy Email report for agency with ID {}'.format(id), exc_info=True, stack_info=True)

        ###
        # Find and mail the https report, if necessary
        #
        # This is very similar to the CyHy block but slightly
        # different.  I need to figure out how to isolate the common
        # functionality into a class or functions.
        ###
        if https_report_dir:
            # The '2' is necessary because in some cases we have both XYZ and
            # XYZ-AB as stakeholders.  Without the '2' the glob would include
            # both for the ID XYZ.
            https_report_glob = '{}/cyhy-{}-2*.pdf'.format(https_report_dir, id)
            https_report_filenames = sorted(glob.glob(https_report_glob))

            # At most one HTTPS report should match
            if len(https_report_filenames) > 1:
                logging.warn('More than one HTTPS report found for agency with ID {}'.format(id))
            elif not https_report_filenames:
                # This is only at info since we are starting from the
                # list of CyHy agencys.  Many of them will not have
                # HTTPS reports.
                logging.info('No HTTPS report found for agency with ID {}'.format(id))

            if https_report_filenames:
                # We take the last filename since, if there happens to be more
                # than one, it should the latest.  (This is because we sorted
                # the glob results.)
                https_attachment_filename = https_report_filenames[-1]

                # Extract the report date from the report filename
                match = re.search(r'-(?P<date>\d{4}-[01]\d-[0-3]\d)-https-report', https_attachment_filename)
                report_date = datetime.datetime.strptime(match.group('date'), '%Y-%m-%d').strftime('%B %d, %Y')

                # Construct the HTTPS message to send
                message = HttpsMessage(to_emails, https_attachment_filename, acronym, report_date)

                try:
                    agencies_emailed_https_reports = send_message(mail_server, message, agencies_emailed_https_reports)
                except (smtplib.SMTPRecipientsRefused, smtplib.SMTPHeloError, smtplib.SMTPSenderRefused, smtplib.SMTPDataError, smtplib.SMTPNotSupportedError):
                    logging.error('Unable to send HTTPS report for agency with ID {}'.format(id), exc_info=True, stack_info=True)

    ###
    # Find and mail the Cybex report, if necessary
    #
    # This is very similar to the CyHy block but slightly different.
    # I need to figure out how to isolate the common functionality
    # into a class or functions.
    ###
    if cybex_scorecard_dir:
        cybex_report_glob = '{}/Federal_Cyber_Exposure_Scorecard-*.pdf'.format(cybex_scorecard_dir)
        cybex_report_filenames = sorted(glob.glob(cybex_report_glob))
        cybex_critical_open_csv_glob = '{}/cybex_open_tickets_critical_*.csv'.format(cybex_scorecard_dir)
        cybex_critical_open_csv_filenames = sorted(glob.glob(cybex_critical_open_csv_glob))
        cybex_critical_closed_csv_glob = '{}/cybex_closed_tickets_critical_*.csv'.format(cybex_scorecard_dir)
        cybex_critical_closed_csv_filenames = sorted(glob.glob(cybex_critical_closed_csv_glob))
        cybex_high_open_csv_glob = '{}/cybex_open_tickets_high_*.csv'.format(cybex_scorecard_dir)
        cybex_high_open_csv_filenames = sorted(glob.glob(cybex_high_open_csv_glob))
        cybex_high_closed_csv_glob = '{}/cybex_closed_tickets_high_*.csv'.format(cybex_scorecard_dir)
        cybex_high_closed_csv_filenames = sorted(glob.glob(cybex_high_closed_csv_glob))

        # At most one Cybex report and CSV should match
        if len(cybex_report_filenames) > 1:
            logging.warn('More than one Cybex report found')
        elif not cybex_report_filenames:
            logging.error('No Cybex report found')
        if len(cybex_critical_open_csv_filenames) > 1:
            logging.warn('More than one Cybex critical open CSV found')
        elif not cybex_critical_open_csv_filenames:
            logging.error('No Cybex critical open CSV found')
        if len(cybex_critical_closed_csv_filenames) > 1:
            logging.warn('More than one Cybex critical closed CSV found')
        elif not cybex_critical_closed_csv_filenames:
            logging.error('No Cybex critical closed CSV found')
        if len(cybex_high_open_csv_filenames) > 1:
            logging.warn('More than one Cybex high open CSV found')
        elif not cybex_high_open_csv_filenames:
            logging.error('No Cybex high open CSV found')
        if len(cybex_high_closed_csv_filenames) > 1:
            logging.warn('More than one Cybex high closed CSV found')
        elif not cybex_high_closed_csv_filenames:
            logging.error('No Cybex high closed CSV found')

        if cybex_report_filenames and cybex_critical_open_csv_filenames and cybex_critical_closed_csv_filenames and cybex_high_open_csv_filenames and cybex_high_closed_csv_filenames:
            # We take the last filename since, if there happens to be more than
            # one, it should the latest.  (This is because we sorted the glob
            # results.)
            cybex_report_filename = cybex_report_filenames[-1]
            cybex_critical_open_csv_filename = cybex_critical_open_csv_filenames[-1]
            cybex_critical_closed_csv_filename = cybex_critical_closed_csv_filenames[-1]
            cybex_high_open_csv_filename = cybex_high_open_csv_filenames[-1]
            cybex_high_closed_csv_filename = cybex_high_closed_csv_filenames[-1]

            # Extract the report date from the report filename
            match = re.search(r'Federal_Cyber_Exposure_Scorecard-(?P<date>\d{4}-[01]\d-[0-3]\d)', cybex_report_filename)
            report_date = datetime.datetime.strptime(match.group('date'), '%Y-%m-%d').strftime('%B %d, %Y')

            # Construct the Cybex message to send
            message = CybexMessage(cybex_report_filename, cybex_critical_open_csv_filename, cybex_critical_closed_csv_filename, cybex_high_open_csv_filename, cybex_high_closed_csv_filename, report_date)

            try:
                cybex_report_emailed = bool(send_message(mail_server, message, 0))
            except (smtplib.SMTPRecipientsRefused, smtplib.SMTPHeloError, smtplib.SMTPSenderRefused, smtplib.SMTPDataError, smtplib.SMTPNotSupportedError):
                logging.error('Unable to send Cybex report', exc_info=True, stack_info=True)

    ###
    # Find and mail the CyHy sample report, if it is present
    ###
    sample_cyhy_report_emailed = False
    if cyhy_report_dir:
        # The '2' is necessary because in some cases we have both XYZ and
        # XYZ-AB as stakeholders.  Without the '2' the glob would include both
        # for the ID XYZ.
        cyhy_sample_report_glob = '{}/cyhy-SAMPLE-2*.pdf'.format(cyhy_report_dir)
        cyhy_sample_report_filenames = sorted(glob.glob(cyhy_sample_report_glob))

        # Exactly one CyHy sample report should match
        if len(cyhy_sample_report_filenames) > 1:
            logging.warn('More than one Cyber Hygiene sample report found')
        elif not cyhy_sample_report_filenames:
            logging.warn('No Cyber Hygiene sample report found')

        if cyhy_sample_report_filenames:
            # We take the last filename since, if there happens to be more than
            # one, it should the latest.  (This is because we sorted the glob
            # results.)
            cyhy_attachment_filename = cyhy_sample_report_filenames[-1]

            # Extract the report date from the report filename
            match = re.search(r'-(?P<date>\d{4}-[01]\d-[0-3]\d)T', cyhy_attachment_filename)
            report_date = datetime.datetime.strptime(match.group('date'), '%Y-%m-%d').strftime('%B %d, %Y')

            # Construct the report message to send
            subject = 'Sample Cyber Hygiene Report - {}'.format(report_date)
            message = ReportMessage(['ncats@hq.dhs.gov'], subject, None, None, cyhy_attachment_filename, cc_addrs=None)

            try:
                sample_cyhy_report_emailed = bool(send_message(mail_server, message, 0))
            except (smtplib.SMTPRecipientsRefused, smtplib.SMTPHeloError, smtplib.SMTPSenderRefused, smtplib.SMTPDataError, smtplib.SMTPNotSupportedError):
                logging.error('Unable to send sample Cyber Hygiene report', exc_info=True, stack_info=True)

    # Print out and log some statistics
    cyhy_stats_string = 'Out of {} Cyber Hygiene agencies, {} ({:.2f}%) were emailed Cyber Hygiene reports.'.format(total_agencies, agencies_emailed_cyhy_reports, 100.0 * agencies_emailed_cyhy_reports / total_agencies)
    tmail_stats_string = 'Out of {} Cyber Hygiene agencies, {} ({:.2f}%) were emailed Trustworthy Email reports.'.format(total_agencies, agencies_emailed_tmail_reports, 100.0 * agencies_emailed_tmail_reports / total_agencies)
    https_stats_string = 'Out of {} Cyber Hygiene agencies, {} ({:.2f}%) were emailed HTTPS reports.'.format(total_agencies, agencies_emailed_https_reports, 100.0 * agencies_emailed_https_reports / total_agencies)
    if cybex_report_emailed:
        cybex_stats_string = 'Cybex report was emailed.'
    else:
        cybex_stats_string = 'Cybex report was not emailed.'
    if sample_cyhy_report_emailed:
        sample_cyhy_stats_string = 'Sample Cyber Hygiene report was emailed.'
    else:
        sample_cyhy_stats_string = 'Sample Cyber Hygiene report was not emailed.'
    logging.info(cyhy_stats_string)
    logging.info(tmail_stats_string)
    logging.info(https_stats_string)
    logging.info(cybex_stats_string)
    logging.info(sample_cyhy_stats_string)
    print(cyhy_stats_string)
    print(tmail_stats_string)
    print(https_stats_string)
    print(cybex_stats_string)
    print(sample_cyhy_stats_string)

    ###
    # Email the summary statistics, if necessary
    ###
    if summary_to:
        message = StatsMessage(summary_to.split(','), [cyhy_stats_string, tmail_stats_string, https_stats_string, cybex_stats_string, sample_cyhy_stats_string])
        try:
            send_message(mail_server, message)
        except (smtplib.SMTPRecipientsRefused, smtplib.SMTPHeloError, smtplib.SMTPSenderRefused, smtplib.SMTPDataError, smtplib.SMTPNotSupportedError):
            logging.error('Unable to send cyhy-mailer report summary', exc_info=True, stack_info=True)


def do_adhoc(db, batch_size, mail_server, to, cyhy, cyhy_federal, subject, html_body, text_body, summary_to):
    """Given the parameters, send out an email to the appropriate
    recipients.

    Parameters
    ----------
    db : MongoDatabase
        The Mongo database from which Cyber Hygiene agency data can
        be retrieved.

    batch_size : int
        The batch size to use when retrieving results from the Mongo
        database.  If None then the default will be used.

    mail_server : smtplib.SMTP
        The mail server via which outgoing mail should be sent.

    to : str
        A comma-separated list of additional email addresses to which
        the ad hoc email message should be sent.  If None then the ad
        hoc email message will not be sent to any additional
        addresses.

    cyhy : bool
        If True then the ad hoc email message will be sent to all
        Cyber Hygiene agencys.

    cyhy_federal : bool
        If True then the ad hoc email message will be sent to all
        Federal Cyber Hygiene agencys.  Note that cyhy implies
        cyhy_federal.

    subject : str
        The subject for the ad hoc email.

    html_body : str
        The filename where the HTML that comprises the body of the ad
        hoc email message can be found.

    text_body : str
        The filename where the plain text that comprises the body of
        the ad hoc email message can be found.

    summary_to : str
        A comma-separated list of email addresses to which the
        summary statistics should be sent at the end of the run.  If
        None then no summary will be sent.
    """
    with open(text_body, 'r') as text_file:
        text = text_file.read()
    with open(html_body, 'r') as html_file:
        html = html_file.read()

    emails = []
    if cyhy:
        try:
            requests = get_cyhy_requests(db, batch_size)
        except TypeError:
            return 4

        for request in requests:
            to_emails = get_emails_from_request(request)
            # to_emails should contain at least one email
            if not to_emails:
                continue

            emails.extend(to_emails)
    elif cyhy_federal:
        try:
            requests = get_federal_cyhy_requests(db)
        except TypeError:
            return 4

        for request in requests:
            to_emails = get_emails_from_request(request)
            # to_emails should contain at least one email
            if not to_emails:
                continue

            emails.extend(to_emails)

    if to:
        emails.extend(to.split(','))

    ad_hoc_emails_to_send = len(emails)
    ad_hoc_emails_sent = 0
    for email in emails:
        message = Message([email], subject, text, html)

        try:
            ad_hoc_emails_sent = send_message(mail_server, message, ad_hoc_emails_sent)
        except (smtplib.SMTPRecipientsRefused, smtplib.SMTPHeloError, smtplib.SMTPSenderRefused, smtplib.SMTPDataError, smtplib.SMTPNotSupportedError):
            logging.error('Unable to send ad hoc email to {}'.format(email), exc_info=True, stack_info=True)

    # Print out and log some statistics
    stats_string = 'Out of {} ad hoc emails to be sent, {} ({:.2f}%) were sent.'.format(ad_hoc_emails_to_send, ad_hoc_emails_sent, 100.0 * ad_hoc_emails_sent / ad_hoc_emails_to_send)
    logging.info(stats_string)
    print(stats_string)

    ###
    # Email the summary statistics, if necessary
    ###
    if summary_to:
        message = StatsMessage(summary_to.split(','), [stats_string])
        try:
            send_message(mail_server, message)
        except (smtplib.SMTPRecipientsRefused, smtplib.SMTPHeloError, smtplib.SMTPSenderRefused, smtplib.SMTPDataError, smtplib.SMTPNotSupportedError):
            logging.error('Unable to send cyhy-mailer ad hoc summary', exc_info=True, stack_info=True)


def main():
    # Parse command line arguments
    args = docopt.docopt(__doc__, version=__version__)

    # Set up logging
    log_level = logging.WARNING
    if args['--debug']:
        log_level = logging.DEBUG
    logging.basicConfig(format='%(asctime)-15s %(levelname)s %(message)s', level=log_level)

    db_creds_file = args['--db-creds-file']
    try:
        db = database_from_config_file(db_creds_file)
    except OSError:
        logging.critical('Database configuration file {} does not exist'.format(db_creds_file), exc_info=True)
        return 1
    except yaml.YAMLError:
        logging.critical('Database configuration file {} does not contain valid YAML'.format(db_creds_file), exc_info=True)
        return 1
    except KeyError:
        logging.critical('Database configuration file {} does not contain the expected keys'.format(db_creds_file), exc_info=True)
        return 1
    except pymongo.errors.ConnectionError:
        logging.critical('Unable to connect to the database server in {}'.format(db_creds_file), exc_info=True)
        return 1
    except pymongo.errors.InvalidName:
        logging.critical('The database in {} does not exist'.format(db_creds_file), exc_info=True)
        return 1

    # Set up the connection to the mail server
    mail_server_hostname = args['--mail-server']
    try:
        mail_server_port = int(args['--mail-port'])
    except ValueError:
        logging.critical('The value {} cannot be interpreted as a valid port'.format(args['--mail-port']), exc_info=True)
        return 2

    try:
        mail_server = smtplib.SMTP(mail_server_hostname, mail_server_port)
        # It would be nice if we could use server.starttls() here, but the
        # postfix server on SMTP01 doesn't yet support it.
    except (smtplib.SMTPConnectError, timeout):
        logging.critical('There was an error connecting to the mail server on port {} of {}'.format(mail_server_port, mail_server_hostname), exc_info=True)
        return 3

    batch_size = args['--batch-size']
    if batch_size is not None:
        try:
            batch_size = int(batch_size)
        except ValueError:
            logging.critical('The value {} cannot be interpreted as an integer'.format(args['--batch-size']), exc_info=True)
            return 4

    if args['report']:
        do_report(db, batch_size, mail_server, args['--cyhy-report-dir'], args['--tmail-report-dir'], args['--https-report-dir'], args['--cybex-scorecard-dir'], args['--summary-to'])
    elif args['adhoc']:
        do_adhoc(db, batch_size, mail_server, args['--to'], args['--cyhy'], args['--cyhy-federal'], args['--subject'], args['--html-body'], args['--text-body'], args['--summary-to'])

    # Close the connection to the mail server
    mail_server.quit()

    # Stop logging and clean up
    logging.shutdown()


if __name__ == '__main__':
    main()
