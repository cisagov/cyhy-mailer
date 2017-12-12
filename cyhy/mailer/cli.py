#!/usr/bin/env python3

"""cyhy-mailer: A tool for mailing out Cyber Hygiene, trustymail, and https-scan reports.

Usage:
  cyhy-mailer [options]
  cyhy-mailer [--cyhy-report-dir=DIRECTORY] [--tmail-report-dir=DIRECTORY] [--https-report-dir=DIRECTORY] [--mail-server=SERVER] [--mail-port=PORT] [--db-creds-file=FILENAME] [--debug]
  cyhy-mailer (-h | --help)

Options:
  -h --help                    Show this message.
  --cyhy-report-dir=DIRECTORY  The directory where the CYHY PDF reports are
                               located.  If not specified then no CYHY reports
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
  -c --db-creds-file=FILENAME  A YAML file containing the CYHY database
                               credentials.
                               [default: /run/secrets/database_creds.yml]
  -d --debug                   A Boolean value indicating whether the output
                               should include debugging messages or not.
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

    try:
        requests = db.requests.find({'retired': {'$ne': True}, 'report_types': 'CYHY'}, {'_id': True, 'agency.acronym': True, 'agency.contacts.email': True, 'agency.contacts.type': True})
    except TypeError:
        logging.critical('There was an error with the MongoDB query that retrieves the list of agencies', exc_info=True)
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

        # Drop any contacts that do not have both a type and an email
        # attribute...
        contacts = [c for c in request['agency']['contacts'] if 'type' in c and 'email' in c]
        # ...but let's log a warning about them
        for c in request['agency']['contacts']:
            if 'type' not in c or 'email' not in c:
                logging.warn('Agency with ID {} has a contact that is missing an email and/or type attribute!'.format(id))

        distro_emails = [c['email'] for c in contacts if c['type'] == 'DISTRO']
        technical_emails = [c['email'] for c in contacts if c['type'] == 'TECHNICAL']

        # There should be zero or one distro email, so log a warning if there
        # are multiple.
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
            continue

        ###
        # Find and mail the CYHY report, if necessary
        ###
        cyhy_report_dir = args['--cyhy-report-dir']
        if cyhy_report_dir:
            cyhy_report_glob = '{}/cyhy-{}-*.pdf'.format(cyhy_report_dir, id)
            cyhy_report_filenames = glob.glob(cyhy_report_glob)

            # Exactly one CYHY report should match
            if len(cyhy_report_filenames) > 1:
                logging.warn('More than one CYHY report found for agency with ID {}'.format(id))
            elif not cyhy_report_filenames:
                # This is an error since we are starting from the list
                # of CYHY customers and they should all have reports
                logging.error('No CYHY report found for agency with ID {}'.format(id))

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
                    logging.error('Unable to send CYHY report for agency with ID {}'.format(id), exc_info=True, stack_info=True)

        ###
        # Find and mail the trustymail report, if necessary
        #
        # This is very similar to the previous block but slightly
        # different.  I need to figure out how to isolate the common
        # functionality into a class or functions.
        ###
        tmail_report_dir = args['--tmail-report-dir']
        if tmail_report_dir:
            tmail_report_glob = '{}/cyhy-{}-*.pdf'.format(tmail_report_dir, id)
            tmail_report_filenames = glob.glob(tmail_report_glob)

            # At most one Tmail report should match
            if len(tmail_report_filenames) > 1:
                logging.warn('More than one Trustworthy Email report found for agency with ID {}'.format(id))
            elif not tmail_report_filenames:
                # This is only at info since we are starting from the
                # list of CYHY customers.  Many of them will not have
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
        # Find the https-scan report, if necessary
        ###
        # https_attachment_filename = None
        # https_report_dir = args['--https-report-dir']
        # if https_report_dir:
        #     https_report_glob = '{}/cyhy-{}-*.pdf'.format(args['--https-report-dir'], id)
        #     https_report_filenames = glob.glob(https_report_glob)

        #     # Exactly one https-scan report should match
        #     if len(https_report_filenames) >= 1:
        #         https_attachment_filename = https_report_filenames[0]
        #         if len(https_report_filenames) > 1:
        #             logging.warn('More than one https-scan report found for agency with ID {}'.format(id))
        #     elif len(https_report_filenames) == 0:
        #         logging.info('No https-scan report found for agency with ID {}'.format(id))

    # Close the connection to the mail server
    mail_server.quit()

    # Print out and log some statistics
    cyhy_stats_string = 'Out of {} CYHY agencies, {} ({:.2f}%) were emailed CYHY reports.'.format(total_agencies, agencies_emailed_cyhy_reports, 100.0 * agencies_emailed_cyhy_reports / total_agencies)
    tmail_stats_string = 'Out of {} CYHY agencies, {} ({:.2f}%) were emailed Trustworthy Email reports.'.format(total_agencies, agencies_emailed_tmail_reports, 100.0 * agencies_emailed_tmail_reports / total_agencies)
    https_stats_string = 'Out of {} CYHY agencies, {} ({:.2f}%) were emailed HTTPS reports.'.format(total_agencies, agencies_emailed_https_reports, 100.0 * agencies_emailed_https_reports / total_agencies)
    logging.info(cyhy_stats_string)
    logging.info(tmail_stats_string)
    logging.info(https_stats_string)
    print(cyhy_stats_string)
    print(tmail_stats_string)
    print(https_stats_string)

    # Stop logging and clean up
    logging.shutdown()


if __name__ == '__main__':
    main()
