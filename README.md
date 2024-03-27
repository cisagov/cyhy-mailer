# cyhy-mailer #

[![Build Status](https://travis-ci.com/cisagov/cyhy-mailer.svg?branch=develop)](https://travis-ci.com/cisagov/cyhy-mailer)
[![Coverage Status](https://coveralls.io/repos/github/cisagov/cyhy-mailer/badge.svg?branch=develop)](https://coveralls.io/github/cisagov/cyhy-mailer?branch=develop)

`cyhy-mailer` is a tool for emailing Cyber Hygiene, `https-scan`, and
`trustymail` reports to the appropriate technical or distribution
e-mail addresses.

## Installation ##

After using `git` to clone the repository, you can install
`cyhy-mailer` using `pip`:

```console
pip install /path/to/cyhy-mailer
```

Or, if you prefer, you can install directly from
[the GitHub repository](https://github.com/cisagov/cyhy-mailer):

```console
pip install git+https://github.com/cisagov/cyhy-mailer.git
```

## Usage ##

```console
Usage:
  cyhy-mailer (bod1801|cybex|cyhy|notification)... [--cyhy-report-dir=DIRECTORY] [--tmail-report-dir=DIRECTORY] [--https-report-dir=DIRECTORY]
[--cybex-scorecard-dir=DIRECTORY] [--cyhy-notification-dir=DIRECTORY]
[--db-creds-file=FILENAME] [--csa-email-file=FILENAME] [--batch-size=SIZE]
[--summary-to=EMAILS] [--debug] [--dry-run]
  cyhy-mailer (-h | --help)

Options:
  -h --help                         Show this message.
  --cyhy-report-dir=DIRECTORY       The directory where the Cyber Hygiene
                                    PDF reports are located.  If not
                                    specified then no Cyber Hygiene reports
                                    will be sent.
  --tmail-report-dir=DIRECTORY      The directory where the trustymail PDF
                                    reports are located.  If not specified then
                                    no trustymail reports will be sent.
  --https-report-dir=DIRECTORY      The directory where the https-scan PDF
                                    reports are located.  If not specified then
                                    no https-scan reports will be sent.
  --cybex-scorecard-dir=DIRECTORY   The directory where the Cybex PDF
                                    scorecard is located.  If not specified
                                    then no Cybex scorecard will be sent.
  --cyhy-notification-dir=DIRECTORY The directory where the Cyber Hygiene
                                    Notification PDF reports are located.  If
                                    not specified then no Cyber Hygiene
                                    notifications will be sent.
  -c --db-creds-file=FILENAME       A YAML file containing the Cyber
                                    Hygiene database credentials.
                                    [default: /run/secrets/database_creds.yml]
  -e --csa-email-file=FILENAME      A YAML file associating each state or
                                    territory with the email address of the
                                    corresponding CISA Cyber Security Advisor
                                    (CSA).  The YAML file should be a
                                    list of dictionaries, each
                                    corresponding to a CSA region.
                                    Each dictionary must contain an
                                    "email" field containing the email
                                    address corresponding to the CSA
                                    for that region, as well as a
                                    "states_and_territories" field
                                    containing a list of two-letter
                                    state and territory abbreviations.
                                    Each abbreviation corresponds to a
                                    state or territory that belongs to
                                    the region.  If this option is
                                    present then the appropriate CSA
                                    will be BCCd any CyHy reports or
                                    notifications related to a
                                    stakeholder within their region.
  --batch-size=SIZE                 The batch size to use when retrieving
                                    results from the Mongo database.  If not
                                    present then the default Mongo batch size
                                    will be used.
  --summary-to=EMAILS               A comma-separated list of email addresses
                                    to which the summary statistics should be
                                    sent at the end of the run.  If not
                                    specified then no summary will be sent.
  -d --debug                        Include debugging messages in the output.
  --dry-run                         Do everything except actually send out
                                    emails.
```

## License ##

This project is in the worldwide [public domain](LICENSE).

This project is in the public domain within the United States, and
copyright and related rights in the work worldwide are waived through
the [CC0 1.0 Universal public domain
dedication](https://creativecommons.org/publicdomain/zero/1.0/).

All contributions to this project will be released under the CC0
dedication. By submitting a pull request, you are agreeing to comply
with this waiver of copyright interest.
