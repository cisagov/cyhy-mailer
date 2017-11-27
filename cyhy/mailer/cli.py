#!/usr/bin/env python3

"""cyhy-mailer: A tool for mailing out Cyber Hygiene, trustymail, and https-scan reports.

Usage:
  cyhy-mailer [options]
  cyhy-mailer [--from=EMAIL_ADDRESS] [--to=EMAIL_ADDRESSES] [--cc=EMAIL_ADDRESSES] [--subject=SUBJECT] [--body=BODY_TEXT] [--attachment=FILENAME] [--mail-server=SERVER] [--debug]
  cyhy-mailer (-h | --help)

Options:
  -h --help                   Show this message.
  -f --from=EMAIL_ADDRESS     The email address that should appear as the
                              sender of the message.
  -t --to=EMAIL_ADDRESSES     A comma-delimited list of email addresses to
                              which the message is being sent.
  -c --cc=EMAIL_ADDRESSES     A comma-delimited list of email addresses to
                              which the message is being carbon copied.
  -s --subject=SUBJECT        The subject of the message.
  -b --body=BODY_TEXT         The body text of the message.
  -a --attachment=FILENAME    The PDF filename to attach to the message.
  -m --mail-server=SERVER     The hostname or IP address of the mail server
                              that should send the message.
  -d --debug                  A Boolean value indicating whether the output
                              should include error and warning messages or not.
"""

import docopt
import logging
import smtplib

from . import __version__
from .CyhyMessage import CyhyMessage
from . import mailer


def main():
    # Parse command line arguments
    args = docopt.docopt(__doc__, version=__version__)

    # Set up logging
    log_level = logging.WARNING
    if args["--debug"]:
        log_level = logging.DEBUG
    logging.basicConfig(format='%(asctime)-15s %(message)s', level=log_level)

    message = CyhyMessage(['jeremy.frasier@beta.dhs.gov'], '/home/jeremy_frasier/artifacts_2017-11-16/reporting/reports/cyhy-DHS-2017-11-16-tmail-report.pdf', cc_addrs=None)

    server = smtplib.SMTP('smtp01.ncats.dhs.gov', 25)
    # server.starttls()
    mailer.send_message(server, message)
    server.quit()

    # Stop logging and clean up
    logging.shutdown()

# TO: Pull DISTRO email from cyhy database; if no DISTRO exists, send to every TECHNICAL POC


if __name__ == '__main__':
    main()
