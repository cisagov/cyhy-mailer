"""This module contains the tests for the CybexMessage class."""

# Standard Python Libraries
import unittest

# cisagov Libraries
from cyhy.mailer.CybexMessage import CybexMessage


class Test(unittest.TestCase):
    """The tests for the CybexMessage class."""

    def test_six_params(self):
        """Test the 6-parameter version of the constructor."""
        pdf = "./tests/data/pdf-sample.pdf"
        csv = "./tests/data/csv-sample.csv"
        report_date = "December 15, 2001"

        message = CybexMessage(pdf, csv, csv, csv, csv, report_date)

        self.assertEqual(message["From"], "reports@cyber.dhs.gov")
        self.assertEqual(
            message["Subject"], "Cyber Exposure Scorecard - December 15, 2001 Results"
        )
        self.assertEqual(message.get("CC"), None)
        self.assertEqual(message["BCC"], "cyhy_reports@hq.dhs.gov")
        self.assertEqual(
            message["To"],
            "CyHy_Reports@hq.dhs.gov,CyberDirectives@cisa.dhs.gov,CyberLiaison@cisa.dhs.gov,cyberscopehelp@cisa.dhs.gov",
        )

        # Grab the bytes that comprise the attachments
        pdf_bytes = open(pdf, "rb").read()
        csv_text = open(csv, "r").read()

        # Make sure the correct body, PDF, and CSV attachments were added
        for part in message.walk():
            # multipart/* are just containers
            if part.get_content_type() == "application/pdf":
                self.assertEqual(part.get_payload(decode=True), pdf_bytes)
                self.assertEqual(part.get_filename(), "pdf-sample.pdf")
            elif part.get_content_type() == "text/plain":
                text_body = """Greetings,

The Cyber Exposure scorecard from December 15, 2001 is attached for your review.

If you have any questions, please contact our office.

Cheers,
CISA Cyber Assessments - Cyber Hygiene
Cybersecurity and Infrastructure Security Agency
vulnerability@cisa.dhs.gov

WARNING: This document is FOR OFFICIAL USE ONLY (FOUO). It contains information that may be exempt from public release under the Freedom of Information Act (5 U.S.G. 552). It is to be controlled, stored, handled, transmitted, distributed, and disposed of in accordance with CISA policy relating to FOUO information and is not to be released to the public or other personnel who do not have a valid 'need-to-know' without prior approval of an authorized CISA official.
"""
                self.assertEqual(part.get_payload(), text_body)
            elif part.get_content_type() == "text/html":
                html_body = """<html>
<head></head>
<body>
<p>Greetings,</p>

<p>The Cyber Exposure scorecard from December 15, 2001 is attached for your
review.</p>

<p>If you have any questions, please contact our office.</p>

<p>Cheers,<br>
CISA Cyber Assessments - Cyber Hygiene<br>
Cybersecurity and Infrastructure Security Agency<br>
<a href="mailto:vulnerability@cisa.dhs.gov">vulnerability@cisa.dhs.gov</a></p>

<p>WARNING: This document is FOR OFFICIAL USE ONLY (FOUO). It contains information that may be exempt from public release under the Freedom of Information Act (5 U.S.G. 552). It is to be controlled, stored, handled, transmitted, distributed, and disposed of in accordance with CISA policy relating to FOUO information and is not to be released to the public or other personnel who do not have a valid 'need-to-know' without prior approval of an authorized CISA official.</p>
</body>
</html>
"""
                self.assertEqual(part.get_payload(), html_body)
            elif part.get_content_type() == "text/csv":
                self.assertEqual(part.get_payload(), csv_text)
                self.assertEqual(part.get_filename(), "csv-sample.csv")

    def test_ten_params(self):
        """Test the 10-parameter version of the constructor."""
        to = ["recipient@example.com", "recipient2@example.com"]
        pdf = "./tests/data/pdf-sample.pdf"
        csv = "./tests/data/csv-sample.csv"
        fm = "sender@example.com"
        cc = ["cc@example.com", "cc2@example.com"]
        bcc = ["bcc@example.com", "bcc2@example.com"]
        report_date = "December 15, 2001"

        message = CybexMessage(
            pdf,
            csv,
            csv,
            csv,
            csv,
            report_date,
            to_addrs=to,
            from_addr=fm,
            cc_addrs=cc,
            bcc_addrs=bcc,
        )

        self.assertEqual(message["From"], fm)
        self.assertEqual(
            message["Subject"], "Cyber Exposure Scorecard - December 15, 2001 Results"
        )
        self.assertEqual(message["CC"], "cc@example.com,cc2@example.com")
        self.assertEqual(message["BCC"], "bcc@example.com,bcc2@example.com")
        self.assertEqual(message["To"], "recipient@example.com,recipient2@example.com")

        # Grab the bytes that comprise the attachments
        pdf_bytes = open(pdf, "rb").read()
        csv_text = open(csv, "r").read()

        # Make sure the correct body, PDF, and CSV attachments were added
        for part in message.walk():
            # multipart/* are just containers
            if part.get_content_type() == "application/pdf":
                self.assertEqual(part.get_payload(decode=True), pdf_bytes)
                self.assertEqual(part.get_filename(), "pdf-sample.pdf")
            elif part.get_content_type() == "text/plain":
                text_body = """Greetings,

The Cyber Exposure scorecard from December 15, 2001 is attached for your review.

If you have any questions, please contact our office.

Cheers,
CISA Cyber Assessments - Cyber Hygiene
Cybersecurity and Infrastructure Security Agency
vulnerability@cisa.dhs.gov

WARNING: This document is FOR OFFICIAL USE ONLY (FOUO). It contains information that may be exempt from public release under the Freedom of Information Act (5 U.S.G. 552). It is to be controlled, stored, handled, transmitted, distributed, and disposed of in accordance with CISA policy relating to FOUO information and is not to be released to the public or other personnel who do not have a valid 'need-to-know' without prior approval of an authorized CISA official.
"""
                self.assertEqual(part.get_payload(), text_body)
            elif part.get_content_type() == "text/html":
                html_body = """<html>
<head></head>
<body>
<p>Greetings,</p>

<p>The Cyber Exposure scorecard from December 15, 2001 is attached for your
review.</p>

<p>If you have any questions, please contact our office.</p>

<p>Cheers,<br>
CISA Cyber Assessments - Cyber Hygiene<br>
Cybersecurity and Infrastructure Security Agency<br>
<a href="mailto:vulnerability@cisa.dhs.gov">vulnerability@cisa.dhs.gov</a></p>

<p>WARNING: This document is FOR OFFICIAL USE ONLY (FOUO). It contains information that may be exempt from public release under the Freedom of Information Act (5 U.S.G. 552). It is to be controlled, stored, handled, transmitted, distributed, and disposed of in accordance with CISA policy relating to FOUO information and is not to be released to the public or other personnel who do not have a valid 'need-to-know' without prior approval of an authorized CISA official.</p>
</body>
</html>
"""
                self.assertEqual(part.get_payload(), html_body)
            elif part.get_content_type() == "text/csv":
                self.assertEqual(part.get_payload(), csv_text)
                self.assertEqual(part.get_filename(), "csv-sample.csv")


if __name__ == "__main__":
    unittest.main()
