#!/usr/bin/env python3

"""cyhy-mailer: A tool for mailing out Cyber Hygiene, trustymail, and https-scan reports.

Usage:
  cyhy-mailer report [options]
  cyhy-mailer report [--cyhy-report-dir=DIRECTORY] [--tmail-report-dir=DIRECTORY] [--https-report-dir=DIRECTORY] [--mail-server=SERVER] [--mail-port=PORT] [--db-creds-file=FILENAME] [--summary-to=EMAILS] [--debug]
  cyhy-mailer adhoc --subject=SUBJECT --html-body=FILENAME --text-body=FILENAME [--to=EMAILS] [--cyhy] [--cyhy-federal] [--mail-server=SERVER] [--mail-port=PORT] [--db-creds-file=FILENAME] [--summary-to=EMAILS] [--debug]
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
  -m --mail-server=SERVER      The hostname or IP address of the mail server
                               that should send the messages.
                               [default: smtp01.ncats.dhs.gov]
  -p --mail-port=PORT          The port to use when connecting to the mail
                               server that should send the messages.
                               [default: 25]
  -c --db-creds-file=FILENAME  A YAML file containing the Cyber
                               Hygiene database credentials.
                               [default: /run/secrets/database_creds.yml]
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
from cyhy.mailer.CyhyMessage import CyhyMessage
from cyhy.mailer.HttpsMessage import HttpsMessage
from cyhy.mailer.Message import Message
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
    # Drop any contacts that do not have both a type and an email
    # attribute...
    contacts = [c for c in request['agency']['contacts'] if 'type' in c and 'email' in c]
    # ...but let's log a warning about them
    for c in request['agency']['contacts']:
        if 'type' not in c or 'email' not in c:
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


def get_cyhy_requests(db):
    """Return a cursor that can be used to iterate over the Cyber Hygiene
    agencies.

    Parameters
    ----------
    db : MongoDatabase
        The Mongo database from which Cyber Hygiene agency data can be
        retrieved.

    Returns
    -------
    pymongo.cursor.Cursor: A cursor that can be used to iterate over
    the Cyber Hygiene agencies.

    Throws
    ------
    pymongo.errors.TypeError: If unable to connect to the requested
    server
    """
    try:
        requests = db.requests.find({'retired': {'$ne': True}, 'report_types': 'CYHY'}, {'_id': True, 'agency.acronym': True, 'agency.contacts.email': True, 'agency.contacts.type': True})
    except TypeError:
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
        requests = db.requests.find({'retired': {'$ne': True}, 'report_types': 'CYHY', 'owner': {'$in': fed_orgs}}, {'_id': True, 'agency.acronym': True, 'agency.contacts.email': True, 'agency.contacts.type': True})
    except TypeError:
        logging.critical('There was an error with the MongoDB query that retrieves the list of agencies', exc_info=True)
        raise

    return requests


def do_report(db, mail_server, cyhy_report_dir, tmail_report_dir, https_report_dir, summary_to):
    """Given the parameters, send out Cyber Hygiene, Trustworthy
    Email, HTTPS reports, and a summary email out as appropriate.

    Parameters
    ----------
    db : MongoDatabase
        The Mongo database from which Cyber Hygiene agency data can
        be retrieved.

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

    summary_to : str
        A comma-separated list of email addresses to which the
        summary statistics should be sent at the end of the run.  If
        None then no summary will be sent.
    """
    try:
        requests = get_cyhy_requests(db)
    except TypeError:
        return 4

    try:
        total_agencies = requests.count()
    except pymongo.errors.OperationFailure:
        logging.critical('Mongo database error while counting the number of request documents returned', exc_info=True)
    agencies_emailed_cyhy_reports = 0
    agencies_emailed_tmail_reports = 0
    agencies_emailed_https_reports = 0
    for request in requests:
        id = request['_id']
        acronym = request['agency']['acronym']

        to_emails = get_emails_from_request(request)
        # to_emails should contain at least one email
        if not to_emails:
            continue

        ###
        # Find and mail the CYHY report, if necessary
        ###
        if cyhy_report_dir:
            cyhy_report_glob = '{}/cyhy-{}-*.pdf'.format(cyhy_report_dir, id)
            cyhy_report_filenames = glob.glob(cyhy_report_glob)

            # Exactly one CYHY report should match
            if len(cyhy_report_filenames) > 1:
                logging.warn('More than one Cyber Hygiene report found for agency with ID {}'.format(id))
            elif not cyhy_report_filenames:
                # This is an error since we are starting from the list
                # of CYHY agencys and they should all have reports
                logging.error('No Cyber Hygiene report found for agency with ID {}'.format(id))

            if cyhy_report_filenames:
                # We take the last filename since, if there happens to
                # be more than one, we hope it is the latest.
                cyhy_attachment_filename = cyhy_report_filenames[-1]

                # Extract the report date from the report filename
                match = re.search(r'-(?P<date>\d{4}-[01]\d-[0-3]\d)T', cyhy_attachment_filename)
                report_date = datetime.datetime.strptime(match.group('date'), '%Y-%m-%d').strftime('%B %d, %Y')

                # Construct the CYHY message to send
                message = CyhyMessage(to_emails, cyhy_attachment_filename, acronym, report_date)

                # "Are you silly?  I'm still gonna send it!"
                #   -- Larry Enticer
                try:
                    mail_server.send_message(message)
                    agencies_emailed_cyhy_reports += 1
                except (smtplib.SMTPRecipientsRefused, smtplib.SMTPHeloError, smtplib.SMTPSenderRefused, smtplib.SMTPDataError, smtplib.SMTPNotSupportedError):
                    # See
                    # https://docs.python.org/3/library/smtplib.html#smtplib.SMTP.sendmail
                    # for a full list of the exceptions that
                    # smtplib.SMTP.send_message can throw.
                    logging.error('Unable to send Cyber Hygiene report for agency with ID {}'.format(id), exc_info=True, stack_info=True)

        ###
        # Find and mail the trustymail report, if necessary
        #
        # This is very similar to the CYHY block but slightly
        # different.  I need to figure out how to isolate the common
        # functionality into a class or functions.
        ###
        if tmail_report_dir:
            tmail_report_glob = '{}/cyhy-{}-*.pdf'.format(tmail_report_dir, id)
            tmail_report_filenames = glob.glob(tmail_report_glob)

            # At most one Tmail report should match
            if len(tmail_report_filenames) > 1:
                logging.warn('More than one Trustworthy Email report found for agency with ID {}'.format(id))
            elif not tmail_report_filenames:
                # This is only at info since we are starting from the
                # list of CYHY agencys.  Many of them will not have
                # Tmail reports.
                logging.info('No Trustworthy Email report found for agency with ID {}'.format(id))

            if tmail_report_filenames:
                # We take the last filename since, if there happens to
                # be more than one, we hope it is the latest.
                tmail_attachment_filename = tmail_report_filenames[-1]

                # Extract the report date from the report filename
                match = re.search(r'-(?P<date>\d{4}-[01]\d-[0-3]\d)-tmail-report', tmail_attachment_filename)
                report_date = datetime.datetime.strptime(match.group('date'), '%Y-%m-%d').strftime('%B %d, %Y')

                # Construct the Tmail message to send
                message = TmailMessage(to_emails, tmail_attachment_filename, acronym, report_date)

                # "Are you silly?  I'm still gonna send it!"
                #   -- Larry Enticer
                try:
                    mail_server.send_message(message)
                    agencies_emailed_tmail_reports += 1
                except (smtplib.SMTPRecipientsRefused, smtplib.SMTPHeloError, smtplib.SMTPSenderRefused, smtplib.SMTPDataError, smtplib.SMTPNotSupportedError):
                    # See
                    # https://docs.python.org/3/library/smtplib.html#smtplib.SMTP.sendmail
                    # for a full list of the exceptions that
                    # smtplib.SMTP.send_message can throw.
                    logging.error('Unable to send Trustworthy Email report for agency with ID {}'.format(id), exc_info=True, stack_info=True)

        ###
        # Find and mail the https report, if necessary
        #
        # This is very similar to the CYHY block but slightly
        # different.  I need to figure out how to isolate the common
        # functionality into a class or functions.
        ###
        if https_report_dir:
            https_report_glob = '{}/cyhy-{}-*.pdf'.format(https_report_dir, id)
            https_report_filenames = glob.glob(https_report_glob)

            # At most one HTTPS report should match
            if len(https_report_filenames) > 1:
                logging.warn('More than one HTTPS report found for agency with ID {}'.format(id))
            elif not https_report_filenames:
                # This is only at info since we are starting from the
                # list of CYHY agencys.  Many of them will not have
                # HTTPS reports.
                logging.info('No HTTPS report found for agency with ID {}'.format(id))

            if https_report_filenames:
                # We take the last filename since, if there happens to
                # be more than one, we hope it is the latest.
                https_attachment_filename = https_report_filenames[-1]

                # Extract the report date from the report filename
                match = re.search(r'-(?P<date>\d{4}-[01]\d-[0-3]\d)-https-report', https_attachment_filename)
                report_date = datetime.datetime.strptime(match.group('date'), '%Y-%m-%d').strftime('%B %d, %Y')

                # Construct the HTTPS message to send
                message = HttpsMessage(to_emails, https_attachment_filename, acronym, report_date)

                # "Are you silly?  I'm still gonna send it!"
                #   -- Larry Enticer
                try:
                    mail_server.send_message(message)
                    agencies_emailed_https_reports += 1
                except (smtplib.SMTPRecipientsRefused, smtplib.SMTPHeloError, smtplib.SMTPSenderRefused, smtplib.SMTPDataError, smtplib.SMTPNotSupportedError):
                    # See
                    # https://docs.python.org/3/library/smtplib.html#smtplib.SMTP.sendmail
                    # for a full list of the exceptions that
                    # smtplib.SMTP.send_message can throw.
                    logging.error('Unable to send HTTPS report for agency with ID {}'.format(id), exc_info=True, stack_info=True)

    # Print out and log some statistics
    cyhy_stats_string = 'Out of {} Cyber Hygiene agencies, {} ({:.2f}%) were emailed Cyber Hygiene reports.'.format(total_agencies, agencies_emailed_cyhy_reports, 100.0 * agencies_emailed_cyhy_reports / total_agencies)
    tmail_stats_string = 'Out of {} Cyber Hygiene agencies, {} ({:.2f}%) were emailed Trustworthy Email reports.'.format(total_agencies, agencies_emailed_tmail_reports, 100.0 * agencies_emailed_tmail_reports / total_agencies)
    https_stats_string = 'Out of {} Cyber Hygiene agencies, {} ({:.2f}%) were emailed HTTPS reports.'.format(total_agencies, agencies_emailed_https_reports, 100.0 * agencies_emailed_https_reports / total_agencies)
    logging.info(cyhy_stats_string)
    logging.info(tmail_stats_string)
    logging.info(https_stats_string)
    print(cyhy_stats_string)
    print(tmail_stats_string)
    print(https_stats_string)

    ###
    # Email the summary statistics, if necessary
    ###
    if summary_to:
        message = StatsMessage(summary_to.split(','), [cyhy_stats_string, tmail_stats_string, https_stats_string])
        try:
            mail_server.send_message(message)
        except (smtplib.SMTPRecipientsRefused, smtplib.SMTPHeloError, smtplib.SMTPSenderRefused, smtplib.SMTPDataError, smtplib.SMTPNotSupportedError):
            # See
            # https://docs.python.org/3/library/smtplib.html#smtplib.SMTP.sendmail
            # for a full list of the exceptions that smtplib.SMTP.send_message
            # can throw.
            logging.error('Unable to send cyhy-mailer summary', exc_info=True, stack_info=True)


def do_adhoc(db, mail_server, to, cyhy, cyhy_federal, subject, html_body, text_body, summary_to):
    """Given the parameters, send out an email to the appropriate
    recipients.

    Parameters
    ----------
    db : MongoDatabase
        The Mongo database from which Cyber Hygiene agency data can
        be retrieved.

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
            requests = get_cyhy_requests(db)
        except TypeError:
            return 4

        for request in requests:
            to_emails = get_emails_from_request(request)
            # to_emails should contain at least one email
            if not to_emails:
                continue

            emails.append(to_emails)
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

            emails.append(to_emails)

    if to:
        emails.append(to.split(','))

    ad_hoc_emails_to_send = len(emails)
    ad_hoc_emails_sent = 0
    for email in emails:
        message = Message([email], subject, text, html)

        # "Are you silly?  I'm still gonna send it!"
        #   -- Larry Enticer
        try:
            mail_server.send_message(message)
            ad_hoc_emails_sent += 1
        except (smtplib.SMTPRecipientsRefused, smtplib.SMTPHeloError, smtplib.SMTPSenderRefused, smtplib.SMTPDataError, smtplib.SMTPNotSupportedError):
            # See
            # https://docs.python.org/3/library/smtplib.html#smtplib.SMTP.sendmail
            # for a full list of the exceptions that
            # smtplib.SMTP.send_message can throw.
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
            mail_server.send_message(message)
        except (smtplib.SMTPRecipientsRefused, smtplib.SMTPHeloError, smtplib.SMTPSenderRefused, smtplib.SMTPDataError, smtplib.SMTPNotSupportedError):
            # See
            # https://docs.python.org/3/library/smtplib.html#smtplib.SMTP.sendmail
            # for a full list of the exceptions that smtplib.SMTP.send_message
            # can throw.
            logging.error('Unable to send cyhy-mailer summary', exc_info=True, stack_info=True)


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

    if args['report']:
        do_report(db, mail_server, args['--cyhy-report-directory'], args['--tmail-report-directory'], args['--https-report-directory'], args['--summary-to'])
    elif args['adhoc']:
        do_adhoc(db, mail_server, args['--to'], args['--cyhy'], args['--cyhy-federal'], args['--subject'], args['--html-body'], args['--text-body'], args['--summary-to'])

    # Close the connection to the mail server
    mail_server.quit()

    # Stop logging and clean up
    logging.shutdown()


if __name__ == '__main__':
    main()
