# cyhy-mailer :postal_horn: :mailbox: #

[![Build Status](https://travis-ci.org/dhs-ncats/cyhy-mailer.svg?branch=develop)](https://travis-ci.org/dhs-ncats/cyhy-mailer)
[![Coverage Status](https://coveralls.io/repos/github/dhs-ncats/cyhy-mailer/badge.svg?branch=develop)](https://coveralls.io/github/dhs-ncats/cyhy-mailer?branch=develop)

`cyhy-mailer` is a tool for emailing Cyber Hygiene, `https-scan`, and
`trustymail` reports to the appropriate technical or distribution
e-mail addresses.

## Installation ##

After using `git` to clone the repository, you can install
`cyhy-mailer` using `pip`:
```bash
pip install /path/to/cyhy-mailer
```

Or, if you prefer, you can install directly from
[the GitHub repository](https://github.com/dhs-ncats/cyhy-mailer):
```bash
pip install git+https://github.com/dhs-ncats/cyhy-mailer.git
```

## Usage ##

```bash
Usage:
  cyhy-mailer report [options]
  cyhy-mailer report [--cyhy-report-dir=DIRECTORY] [--tmail-report-dir=DIRECTORY] [--https-report-dir=DIRECTORY] [--cybex-report-dir=DIRECTORY] [--mail-server=SERVER] [--mail-port=PORT] [--db-creds-file=FILENAME] [--summary-to=EMAILS] [--debug]
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
  --cybex-report-dir=DIRECTORY The directory where the Cybex PDF
                               report is located.  If not specified
                               then no Cybex report will be sent.
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
```

## License ##

This project is in the worldwide [public domain](LICENSE.md).

This project is in the public domain within the United States, and
copyright and related rights in the work worldwide are waived through
the [CC0 1.0 Universal public domain
dedication](https://creativecommons.org/publicdomain/zero/1.0/).

All contributions to this project will be released under the CC0
dedication. By submitting a pull request, you are agreeing to comply
with this waiver of copyright interest.
