#!/usr/bin/env python3

"""cyhy-mailer: A tool for mailing out Cyber Hygiene, trustymail, and https-scan reports.

Usage:
  cyhy-mailer [options]
  cyhy-mailer (--cyhy-report-dir=DIRECTORY) (--financial-year=YEAR) (--fy-quarter=QUARTER) [--mail-server=SERVER] [--mail-port=PORT] [--db-creds-file=FILENAME] [--debug]
  cyhy-mailer (-h | --help)

Options:
  -h --help                   Show this message.
  --cyhy-report-dir=DIRECTORY The directory where the CYHY PDF reports are
                              located.
  -y --financial-year=YEAR    The four-digit financial year to which the 
                              reports being mailed out correspond.
  -q --fy-quarter=QUARTER     The quarter of the financial year to which the
                              reports being mailed out correspond.  Expected
                              values are 1, 2, 3, or 4.
  -m --mail-server=SERVER     The hostname or IP address of the mail server
                              that should send the messages. 
                              [default: smtp01.ncats.dhs.gov]
  -p --mail-port=PORT         The port to use when connecting to the mail
                              server that should send the messages.
                              [default: 25]
  -c --db-creds-file=FILENAME A YAML file containing the CYHY database
                              credentials.
                              [default: /run/secrets/database_creds.yml]
  -d --debug                  A Boolean value indicating whether the output
                              should include debugging messages or not.
"""

import docopt
import glob
import logging
import smtplib

from pymongo import MongoClient
import yaml

from . import __version__
from .CyhyMessage import CyhyMessage


def database_from_config_file(config_filename):
    with open(config_filename, 'r') as stream:
        config = yaml.load(stream)

    try:
        db_uri = config['database']['uri']
        db_name = config['database']['name']
    except:
        logging.error('Incorrect database config file format in {}'.format(config_filename), exc_info=True)

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

    db = database_from_config_file(args['--db-creds-file'])

    # Set up the connection to the mail server
    server = smtplib.SMTP(args['--mail-server'], int(args['--mail-port']))
    # server.starttls()

    requests = db.requests.find({'retired': False}, {'_id': True, 'agency.acronym': True, 'agency.contacts.email': True, 'agency.contacts.type': True})

    total_agencies = requests.count()
    agencies_emailed = 0
    for request in requests:
        id = request['_id']
        acronym = request['agency']['acronym']

        # Drop any contacts that do not have both a type and an email attribute...
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

        cyhy_report_glob = '{}/cyhy-{}-*.pdf'.format(args['--cyhy-report-dir'], id)
        cyhy_report_filenames = glob.glob(cyhy_report_glob)

        # Exactly one CYHY report should match
        if len(cyhy_report_filenames) > 1:
            logging.warn('More than one CYHY report found for agency with ID {}'.format(id))
            continue
        elif len(cyhy_report_filenames) == 0:
            logging.error('No CYHY report found for agency with ID {}'.format(id))
            continue

        attachment_filename = cyhy_report_filenames[0]

        message = CyhyMessage(to_emails, attachment_filename, acronym, args['--financial-year'], args['--fy-quarter'])

        # mailer.send_message(server, message)
        agencies_emailed += 1

    server.quit()

    # Print out and log some statistics
    stats_string = 'Out of {} agencies, {} ({}%) were emailed.'.format(total_agencies, agencies_emailed, 100.0 * agencies_emailed / total_agencies)
    logging.info(stats_string)
    print(stats_string)

    # Stop logging and clean up
    logging.shutdown()


if __name__ == '__main__':
    main()
