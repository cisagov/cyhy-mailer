#!/usr/bin/env python3

"""preview_messages: Render cyhy-mailer email messages for review.

Each selected message type is built from its real message class with
sample data, and the plain text and HTML bodies are written to the
output directory.  Every variant of a message type is rendered, e.g.
the Cyber Hygiene report with and without technical POCs.  If no
message types are given then all of them are rendered.

Usage:
  preview_messages.py [(cybex|cyhy|https|notification|summary|tmail)...] [--output-dir=DIRECTORY]
  preview_messages.py (-h | --help)

Message types:
  cybex         Cyber Exposure scorecard
  cyhy          Cyber Hygiene report, with and without technical POCs
  https         HTTPS report
  notification  Cyber Hygiene notification, Federal and non-Federal
  summary       cyhy-mailer summary statistics
  tmail         Trustworthy Email report

Options:
  -h --help                     Show this message.
  -o --output-dir=DIRECTORY     The directory where the previews are
                                written.  [default: previews]

"""

# Standard Python Libraries
import datetime
from pathlib import Path

# Third-Party Libraries
import docopt

# cisagov Libraries
from cyhy.mailer.CybexMessage import CybexMessage
from cyhy.mailer.CyhyMessage import CyhyMessage
from cyhy.mailer.CyhyNotificationMessage import CyhyNotificationMessage
from cyhy.mailer.HttpsMessage import HttpsMessage
from cyhy.mailer.StatsMessage import StatsMessage
from cyhy.mailer.TmailMessage import TmailMessage

TEST_DATA_DIR = Path(__file__).resolve().parent / "tests" / "data"
PDF_FILENAME = str(TEST_DATA_DIR / "pdf-sample.pdf")
CSV_FILENAME = str(TEST_DATA_DIR / "csv-sample.csv")

TO_ADDRS = ["recipient@example.com"]
ENTITY_ACRONYM = "TEST"
ENTITY_NAME = "Test Organization"
TECH_POCS = [
    {"name": "Test POC One", "email": "poc1@example.com"},
    {"name": "Test POC Two", "email": "poc2@example.com"},
]
SUMMARY_STRINGS = [
    "Out of 100 Federal BOD 18-01 entities, 95 (95.00%) were emailed Trustworthy Email reports.",
    "Out of 100 Federal BOD 18-01 entities, 95 (95.00%) were emailed HTTPS reports.",
    "Cyber Exposure scorecard was emailed.",
    "Out of 200 Cyber Hygiene entities, 190 (95.00%) were emailed Cyber Hygiene reports.",
    "Sample Cyber Hygiene report was emailed.",
    "Out of 200 Cyber Hygiene entities, 10 (5.00%) were emailed Cyber Hygiene notifications.",
]

BODY_EXTENSIONS = {"text/plain": "txt", "text/html": "html"}


def cybex_previews(report_date):
    """Return the Cyber Exposure scorecard preview."""
    message = CybexMessage(
        PDF_FILENAME,
        CSV_FILENAME,
        CSV_FILENAME,
        CSV_FILENAME,
        CSV_FILENAME,
        report_date,
        to_addrs=TO_ADDRS,
    )
    return [("cybex_scorecard", message)]


def cyhy_previews(report_date):
    """Return the Cyber Hygiene report previews."""
    return [
        (
            f"cyhy_report_{suffix}",
            CyhyMessage(
                TO_ADDRS,
                PDF_FILENAME,
                ENTITY_ACRONYM,
                ENTITY_NAME,
                report_date,
                tech_pocs,
            ),
        )
        for suffix, tech_pocs in (("with_pocs", TECH_POCS), ("no_pocs", []))
    ]


def https_previews(report_date):
    """Return the HTTPS report preview."""
    message = HttpsMessage(
        TO_ADDRS, PDF_FILENAME, ENTITY_ACRONYM, ENTITY_NAME, report_date
    )
    return [("https_report", message)]


def notification_previews(report_date):
    """Return the Cyber Hygiene notification previews."""
    return [
        (
            f"cyhy_notification_{suffix}",
            CyhyNotificationMessage(
                TO_ADDRS,
                PDF_FILENAME,
                ENTITY_ACRONYM,
                ENTITY_NAME,
                is_federal,
                report_date,
            ),
        )
        for suffix, is_federal in (("federal", True), ("nonfederal", False))
    ]


def summary_previews(report_date):
    """Return the cyhy-mailer summary statistics preview."""
    # StatsMessage stamps itself with the current time.
    return [("cyhy_mailer_summary", StatsMessage(TO_ADDRS, SUMMARY_STRINGS))]


def tmail_previews(report_date):
    """Return the Trustworthy Email report preview."""
    message = TmailMessage(
        TO_ADDRS, PDF_FILENAME, ENTITY_ACRONYM, ENTITY_NAME, report_date
    )
    return [("tmail_report", message)]


PREVIEWS = {
    "cybex": cybex_previews,
    "cyhy": cyhy_previews,
    "https": https_previews,
    "notification": notification_previews,
    "summary": summary_previews,
    "tmail": tmail_previews,
}


def write_bodies(message, output_dir, name):
    """Write the plain text and HTML bodies of a message to files.

    Parameters
    ----------
    message : Message
        The message whose bodies are to be written.

    output_dir : Path
        The directory where the files are written.

    name : str
        The base name of the files.

    Returns
    -------
    list of Path: The files that were written.

    """
    written = []
    for part in message.walk():
        extension = BODY_EXTENSIONS.get(part.get_content_type())
        if extension is None:
            continue
        charset = part.get_content_charset() or "utf-8"
        body = part.get_payload(decode=True).decode(charset)
        path = output_dir / f"{name}.{extension}"
        path.write_text(body, encoding="utf-8")
        written.append(path)
    return written


def main():
    """Render the selected message previews."""
    args = docopt.docopt(__doc__)

    selected = [t for t in PREVIEWS if args[t]] or list(PREVIEWS)
    output_dir = Path(args["--output-dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    # Match the report date format used by cyhy-mailer.
    report_date = datetime.date.today().strftime("%B %d, %Y")

    for message_type in selected:
        for name, message in PREVIEWS[message_type](report_date):
            print(f"{name}: {message['Subject']}")
            for path in write_bodies(message, output_dir, name):
                print(f"  {path}")


if __name__ == "__main__":
    main()
