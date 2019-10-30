"""This module contains the tests for the CyhyMessage class."""

import unittest

from cyhy.mailer.CyhyMessage import CyhyMessage


class Test(unittest.TestCase):
    """The tests for the CyhyMessage class."""

    def test_four_params_single_recipient_no_pocs(self):
        """Test the 4-parameter version of the constructor."""
        to = ["recipient@example.com"]
        pdf = "./tests/data/pdf-sample.pdf"
        agency_acronym = "CLARKE"
        report_date = "December 15, 2001"
        tech_pocs = []

        message = CyhyMessage(to, pdf, agency_acronym, report_date, tech_pocs)

        self.assertEqual(message["From"], "reports@cyber.dhs.gov")
        self.assertEqual(
            message["Subject"],
            "CLARKE - Cyber Hygiene Report - December 15, 2001 Results",
        )
        self.assertEqual(message.get("CC"), None)
        self.assertEqual(message["BCC"], None)
        self.assertEqual(message["To"], "recipient@example.com")

        # Grab the bytes that comprise the attachment
        bytes = open(pdf, "rb").read()

        # Make sure the correct body and PDF attachments were added
        for part in message.walk():
            # multipart/* are just containers
            if part.get_content_type() == "application/pdf":
                self.assertEqual(part.get_payload(decode=True), bytes)
                self.assertEqual(part.get_filename(), "pdf-sample.pdf")
            elif part.get_content_type() == "text/plain":
                text_body = """Greetings CLARKE,

The Cyber Hygiene scan results are attached for your review. Same password as before. (If this is your first report and you have yet to receive a password, please let us know.)

If you have any questions, please contact our office.

Cheers,
The NCATS team

National Cybersecurity Assessments and Technical Services (NCATS)
Cybersecurity and Infrastructure Security Agency (CISA)
ncats@hq.dhs.gov

WARNING: This document is FOR OFFICIAL USE ONLY (FOUO). It contains information that may be exempt from public release under the Freedom of Information Act (5 U.S.G. 552). It is to be controlled, stored, handled, transmitted, distributed, and disposed of in accordance with CISA policy relating to FOUO information and is not to be released to the public or other personnel who do not have a valid 'need-to-know' without prior approval of an authorized CISA official.
"""
                self.assertEqual(part.get_payload(), text_body)
            elif part.get_content_type() == "text/html":
                html_body = """<html>
<head></head>
<body>
<p>Greetings CLARKE,</p>

<p>The Cyber Hygiene scan results are attached for your review. Same password as before. (If this is your first report and you have yet to receive a password, please let us know.)</p>

<p>If you have any questions, please contact our office.</p>

<p>Cheers,<br>
The NCATS team</p>

<p>National Cybersecurity Assessments and Technical Services (NCATS)<br>
Cybersecurity and Infrastructure Security Agency (CISA)<br>
<a href="mailto:ncats@hq.dhs.gov">ncats@hq.dhs.gov</a></p>

<p>WARNING: This document is FOR OFFICIAL USE ONLY (FOUO). It contains information that may be exempt from public release under the Freedom of Information Act (5 U.S.G. 552). It is to be controlled, stored, handled, transmitted, distributed, and disposed of in accordance with CISA policy relating to FOUO information and is not to be released to the public or other personnel who do not have a valid 'need-to-know' without prior approval of an authorized CISA official.</p>
</body>
</html>
"""
                self.assertEqual(part.get_payload(), html_body)

    def test_four_params_single_recipient_multiple_pocs(self):
        """Test the 4-parameter version of the constructor."""
        to = ["recipient@example.com"]
        pdf = "./tests/data/pdf-sample.pdf"
        agency_acronym = "CLARKE"
        report_date = "December 15, 2001"
        tech_pocs = [
            {"name": "Cixin Liu", "email": "cixin@liu.com"},
            {"name": "Alastair Reynolds", "email": "alastair@reynolds.com"},
        ]

        message = CyhyMessage(to, pdf, agency_acronym, report_date, tech_pocs)

        self.assertEqual(message["From"], "reports@cyber.dhs.gov")
        self.assertEqual(
            message["Subject"],
            "CLARKE - Cyber Hygiene Report - December 15, 2001 Results",
        )
        self.assertEqual(message.get("CC"), None)
        self.assertEqual(message["BCC"], None)
        self.assertEqual(message["To"], "recipient@example.com")

        # Grab the bytes that comprise the attachment
        bytes = open(pdf, "rb").read()

        # Make sure the correct body and PDF attachments were added
        for part in message.walk():
            # multipart/* are just containers
            if part.get_content_type() == "application/pdf":
                self.assertEqual(part.get_payload(decode=True), bytes)
                self.assertEqual(part.get_filename(), "pdf-sample.pdf")
            elif part.get_content_type() == "text/plain":
                text_body = """Greetings CLARKE,

The Cyber Hygiene scan results are attached for your review. Same password as before. (If this is your first report and you have yet to receive a password, please let us know.)

Note: NCATS has the following information listed as the Technical Points of Contact for CLARKE:

Name:  Cixin Liu
Email:  cixin@liu.com

Name:  Alastair Reynolds
Email:  alastair@reynolds.com

Please request the report password from a Technical Point of Contact and route all other requests through a Technical POC. Should a Technical Point of Contact listed above no longer be with CLARKE, please contact NCATS@hq.dhs.gov with updated information.

If you have any questions, please contact our office.

Cheers,
The NCATS team

National Cybersecurity Assessments and Technical Services (NCATS)
Cybersecurity and Infrastructure Security Agency (CISA)
ncats@hq.dhs.gov

WARNING: This document is FOR OFFICIAL USE ONLY (FOUO). It contains information that may be exempt from public release under the Freedom of Information Act (5 U.S.G. 552). It is to be controlled, stored, handled, transmitted, distributed, and disposed of in accordance with CISA policy relating to FOUO information and is not to be released to the public or other personnel who do not have a valid 'need-to-know' without prior approval of an authorized CISA official.
"""
                self.assertEqual(part.get_payload(), text_body)
            elif part.get_content_type() == "text/html":
                html_body = """<html>
<head></head>
<body>
<p>Greetings CLARKE,</p>

<p>The Cyber Hygiene scan results are attached for your review. Same password as before. (If this is your first report and you have yet to receive a password, please let us know.)</p>

<p>Note: NCATS has the following information listed as the Technical Points of Contact for CLARKE:</p>

<p>
Name:  Cixin Liu<br>
Email:  cixin@liu.com<br>
</p>
<p>
Name:  Alastair Reynolds<br>
Email:  alastair@reynolds.com<br>
</p>

<p>Please request the report password from a Technical Point of Contact and route all other requests through a Technical POC. Should a Technical Point of Contact listed above no longer be with CLARKE, please contact <a href="mailto:NCATS@hq.dhs.gov">NCATS@hq.dhs.gov</a> with updated information.</p>

<p>If you have any questions, please contact our office.</p>

<p>Cheers,<br>
The NCATS team</p>

<p>National Cybersecurity Assessments and Technical Services (NCATS)<br>
Cybersecurity and Infrastructure Security Agency (CISA)<br>
<a href="mailto:ncats@hq.dhs.gov">ncats@hq.dhs.gov</a></p>

<p>WARNING: This document is FOR OFFICIAL USE ONLY (FOUO). It contains information that may be exempt from public release under the Freedom of Information Act (5 U.S.G. 552). It is to be controlled, stored, handled, transmitted, distributed, and disposed of in accordance with CISA policy relating to FOUO information and is not to be released to the public or other personnel who do not have a valid 'need-to-know' without prior approval of an authorized CISA official.</p>
</body>
</html>
"""
                self.assertEqual(part.get_payload(), html_body)

    def test_four_params_multiple_recipients_one_poc(self):
        """Test the 4-parameter version of the constructor."""
        to = ["recipient@example.com", "recipient2@example.com"]
        pdf = "./tests/data/pdf-sample.pdf"
        agency_acronym = "CLARKE"
        report_date = "December 15, 2001"
        tech_pocs = [{"name": "Cixin Liu", "email": "cixin@liu.com"}]

        message = CyhyMessage(to, pdf, agency_acronym, report_date, tech_pocs)

        self.assertEqual(message["From"], "reports@cyber.dhs.gov")
        self.assertEqual(
            message["Subject"],
            "CLARKE - Cyber Hygiene Report - December 15, 2001 Results",
        )
        self.assertEqual(message.get("CC"), None)
        self.assertEqual(message["BCC"], None)
        self.assertEqual(message["To"], "recipient@example.com,recipient2@example.com")

        # Grab the bytes that comprise the attachment
        bytes = open(pdf, "rb").read()

        # Make sure the correct body and PDF attachments were added
        for part in message.walk():
            # multipart/* are just containers
            if part.get_content_type() == "application/pdf":
                self.assertEqual(part.get_payload(decode=True), bytes)
                self.assertEqual(part.get_filename(), "pdf-sample.pdf")
            elif part.get_content_type() == "text/plain":
                body = """Greetings CLARKE,

The Cyber Hygiene scan results are attached for your review. Same password as before. (If this is your first report and you have yet to receive a password, please let us know.)

Note: NCATS has the following information listed as the Technical Points of Contact for CLARKE:

Name:  Cixin Liu
Email:  cixin@liu.com

Please request the report password from a Technical Point of Contact and route all other requests through a Technical POC. Should a Technical Point of Contact listed above no longer be with CLARKE, please contact NCATS@hq.dhs.gov with updated information.

If you have any questions, please contact our office.

Cheers,
The NCATS team

National Cybersecurity Assessments and Technical Services (NCATS)
Cybersecurity and Infrastructure Security Agency (CISA)
ncats@hq.dhs.gov

WARNING: This document is FOR OFFICIAL USE ONLY (FOUO). It contains information that may be exempt from public release under the Freedom of Information Act (5 U.S.G. 552). It is to be controlled, stored, handled, transmitted, distributed, and disposed of in accordance with CISA policy relating to FOUO information and is not to be released to the public or other personnel who do not have a valid 'need-to-know' without prior approval of an authorized CISA official.
"""
                self.assertEqual(part.get_payload(), body)
            elif part.get_content_type() == "text/html":
                html_body = """<html>
<head></head>
<body>
<p>Greetings CLARKE,</p>

<p>The Cyber Hygiene scan results are attached for your review. Same password as before. (If this is your first report and you have yet to receive a password, please let us know.)</p>

<p>Note: NCATS has the following information listed as the Technical Points of Contact for CLARKE:</p>

<p>
Name:  Cixin Liu<br>
Email:  cixin@liu.com<br>
</p>

<p>Please request the report password from a Technical Point of Contact and route all other requests through a Technical POC. Should a Technical Point of Contact listed above no longer be with CLARKE, please contact <a href="mailto:NCATS@hq.dhs.gov">NCATS@hq.dhs.gov</a> with updated information.</p>

<p>If you have any questions, please contact our office.</p>

<p>Cheers,<br>
The NCATS team</p>

<p>National Cybersecurity Assessments and Technical Services (NCATS)<br>
Cybersecurity and Infrastructure Security Agency (CISA)<br>
<a href="mailto:ncats@hq.dhs.gov">ncats@hq.dhs.gov</a></p>

<p>WARNING: This document is FOR OFFICIAL USE ONLY (FOUO). It contains information that may be exempt from public release under the Freedom of Information Act (5 U.S.G. 552). It is to be controlled, stored, handled, transmitted, distributed, and disposed of in accordance with CISA policy relating to FOUO information and is not to be released to the public or other personnel who do not have a valid 'need-to-know' without prior approval of an authorized CISA official.</p>
</body>
</html>
"""
                self.assertEqual(part.get_payload(), html_body)

    def test_six_params_single_cc_one_poc(self):
        """Test the 6-parameter version of the constructor."""
        to = ["recipient@example.com", "recipient2@example.com"]
        pdf = "./tests/data/pdf-sample.pdf"
        fm = "sender@example.com"
        cc = ["cc@example.com"]
        bcc = ["bcc@example.com"]
        agency_acronym = "CLARKE"
        report_date = "December 15, 2001"
        tech_pocs = [{"name": "Cixin Liu", "email": "cixin@liu.com"}]

        message = CyhyMessage(
            to,
            pdf,
            agency_acronym,
            report_date,
            tech_pocs,
            from_addr=fm,
            cc_addrs=cc,
            bcc_addrs=bcc,
        )

        self.assertEqual(message["From"], fm)
        self.assertEqual(
            message["Subject"],
            "CLARKE - Cyber Hygiene Report - December 15, 2001 Results",
        )
        self.assertEqual(message["CC"], "cc@example.com")
        self.assertEqual(message["BCC"], "bcc@example.com")
        self.assertEqual(message["To"], "recipient@example.com,recipient2@example.com")

        # Grab the bytes that comprise the attachment
        bytes = open(pdf, "rb").read()

        # Make sure the correct body and PDF attachments were added
        for part in message.walk():
            # multipart/* are just containers
            if part.get_content_type() == "application/pdf":
                self.assertEqual(part.get_payload(decode=True), bytes)
                self.assertEqual(part.get_filename(), "pdf-sample.pdf")
            elif part.get_content_type() == "text/plain":
                body = """Greetings CLARKE,

The Cyber Hygiene scan results are attached for your review. Same password as before. (If this is your first report and you have yet to receive a password, please let us know.)

Note: NCATS has the following information listed as the Technical Points of Contact for CLARKE:

Name:  Cixin Liu
Email:  cixin@liu.com

Please request the report password from a Technical Point of Contact and route all other requests through a Technical POC. Should a Technical Point of Contact listed above no longer be with CLARKE, please contact NCATS@hq.dhs.gov with updated information.

If you have any questions, please contact our office.

Cheers,
The NCATS team

National Cybersecurity Assessments and Technical Services (NCATS)
Cybersecurity and Infrastructure Security Agency (CISA)
ncats@hq.dhs.gov

WARNING: This document is FOR OFFICIAL USE ONLY (FOUO). It contains information that may be exempt from public release under the Freedom of Information Act (5 U.S.G. 552). It is to be controlled, stored, handled, transmitted, distributed, and disposed of in accordance with CISA policy relating to FOUO information and is not to be released to the public or other personnel who do not have a valid 'need-to-know' without prior approval of an authorized CISA official.
"""
                self.assertEqual(part.get_payload(), body)
            elif part.get_content_type() == "text/html":
                html_body = """<html>
<head></head>
<body>
<p>Greetings CLARKE,</p>

<p>The Cyber Hygiene scan results are attached for your review. Same password as before. (If this is your first report and you have yet to receive a password, please let us know.)</p>

<p>Note: NCATS has the following information listed as the Technical Points of Contact for CLARKE:</p>

<p>
Name:  Cixin Liu<br>
Email:  cixin@liu.com<br>
</p>

<p>Please request the report password from a Technical Point of Contact and route all other requests through a Technical POC. Should a Technical Point of Contact listed above no longer be with CLARKE, please contact <a href="mailto:NCATS@hq.dhs.gov">NCATS@hq.dhs.gov</a> with updated information.</p>

<p>If you have any questions, please contact our office.</p>

<p>Cheers,<br>
The NCATS team</p>

<p>National Cybersecurity Assessments and Technical Services (NCATS)<br>
Cybersecurity and Infrastructure Security Agency (CISA)<br>
<a href="mailto:ncats@hq.dhs.gov">ncats@hq.dhs.gov</a></p>

<p>WARNING: This document is FOR OFFICIAL USE ONLY (FOUO). It contains information that may be exempt from public release under the Freedom of Information Act (5 U.S.G. 552). It is to be controlled, stored, handled, transmitted, distributed, and disposed of in accordance with CISA policy relating to FOUO information and is not to be released to the public or other personnel who do not have a valid 'need-to-know' without prior approval of an authorized CISA official.</p>
</body>
</html>
"""
                self.assertEqual(part.get_payload(), html_body)

    def test_six_params_multiple_cc_one_poc(self):
        """Test the 6-parameter version of the constructor."""
        to = ["recipient@example.com", "recipient2@example.com"]
        pdf = "./tests/data/pdf-sample.pdf"
        fm = "sender@example.com"
        cc = ["cc@example.com", "cc2@example.com"]
        bcc = ["bcc@example.com", "bcc2@example.com"]
        agency_acronym = "CLARKE"
        report_date = "December 15, 2001"
        tech_pocs = [{"name": "Cixin Liu", "email": "cixin@liu.com"}]

        message = CyhyMessage(
            to,
            pdf,
            agency_acronym,
            report_date,
            tech_pocs,
            from_addr=fm,
            cc_addrs=cc,
            bcc_addrs=bcc,
        )

        self.assertEqual(message["From"], fm)
        self.assertEqual(
            message["Subject"],
            "CLARKE - Cyber Hygiene Report - December 15, 2001 Results",
        )
        self.assertEqual(message["CC"], "cc@example.com,cc2@example.com")
        self.assertEqual(message["BCC"], "bcc@example.com,bcc2@example.com")
        self.assertEqual(message["To"], "recipient@example.com,recipient2@example.com")

        # Grab the bytes that comprise the attachment
        bytes = open(pdf, "rb").read()

        # Make sure the correct body and PDF attachments were added
        for part in message.walk():
            # multipart/* are just containers
            if part.get_content_type() == "application/pdf":
                self.assertEqual(part.get_payload(decode=True), bytes)
                self.assertEqual(part.get_filename(), "pdf-sample.pdf")
            elif part.get_content_type() == "text/plain":
                body = """Greetings CLARKE,

The Cyber Hygiene scan results are attached for your review. Same password as before. (If this is your first report and you have yet to receive a password, please let us know.)

Note: NCATS has the following information listed as the Technical Points of Contact for CLARKE:

Name:  Cixin Liu
Email:  cixin@liu.com

Please request the report password from a Technical Point of Contact and route all other requests through a Technical POC. Should a Technical Point of Contact listed above no longer be with CLARKE, please contact NCATS@hq.dhs.gov with updated information.

If you have any questions, please contact our office.

Cheers,
The NCATS team

National Cybersecurity Assessments and Technical Services (NCATS)
Cybersecurity and Infrastructure Security Agency (CISA)
ncats@hq.dhs.gov

WARNING: This document is FOR OFFICIAL USE ONLY (FOUO). It contains information that may be exempt from public release under the Freedom of Information Act (5 U.S.G. 552). It is to be controlled, stored, handled, transmitted, distributed, and disposed of in accordance with CISA policy relating to FOUO information and is not to be released to the public or other personnel who do not have a valid 'need-to-know' without prior approval of an authorized CISA official.
"""
                self.assertEqual(part.get_payload(), body)
            elif part.get_content_type() == "text/html":
                html_body = """<html>
<head></head>
<body>
<p>Greetings CLARKE,</p>

<p>The Cyber Hygiene scan results are attached for your review. Same password as before. (If this is your first report and you have yet to receive a password, please let us know.)</p>

<p>Note: NCATS has the following information listed as the Technical Points of Contact for CLARKE:</p>

<p>
Name:  Cixin Liu<br>
Email:  cixin@liu.com<br>
</p>

<p>Please request the report password from a Technical Point of Contact and route all other requests through a Technical POC. Should a Technical Point of Contact listed above no longer be with CLARKE, please contact <a href="mailto:NCATS@hq.dhs.gov">NCATS@hq.dhs.gov</a> with updated information.</p>

<p>If you have any questions, please contact our office.</p>

<p>Cheers,<br>
The NCATS team</p>

<p>National Cybersecurity Assessments and Technical Services (NCATS)<br>
Cybersecurity and Infrastructure Security Agency (CISA)<br>
<a href="mailto:ncats@hq.dhs.gov">ncats@hq.dhs.gov</a></p>

<p>WARNING: This document is FOR OFFICIAL USE ONLY (FOUO). It contains information that may be exempt from public release under the Freedom of Information Act (5 U.S.G. 552). It is to be controlled, stored, handled, transmitted, distributed, and disposed of in accordance with CISA policy relating to FOUO information and is not to be released to the public or other personnel who do not have a valid 'need-to-know' without prior approval of an authorized CISA official.</p>
</body>
</html>
"""
                self.assertEqual(part.get_payload(), html_body)


if __name__ == "__main__":
    unittest.main()
