"""This module contains the tests for the CyhyNotificationMessage class."""

import unittest

from cyhy.mailer.CyhyNotificationMessage import CyhyNotificationMessage


class Test(unittest.TestCase):
    """The tests for the CyhyNotificationMessage class."""

    def test_four_params_single_recipient_fed(self):
        """Test the 4-parameter Federal version of the constructor."""
        to = ["recipient@example.com"]
        pdf = "./tests/data/pdf-sample.pdf"
        agency_acronym = "FEDTEST"
        is_federal = True
        report_date = "December 15, 2001"

        message = CyhyNotificationMessage(
            to, pdf, agency_acronym, is_federal, report_date
        )

        self.assertEqual(message["From"], "reports@cyber.dhs.gov")
        self.assertEqual(
            message["Subject"],
            "FEDTEST - Cyber Hygiene Alert - December 15, 2001",
        )
        self.assertEqual(message.get("CC"), None)
        self.assertEqual(message["BCC"], "cyhy_reports@hq.dhs.gov")
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
                text_body = """Greetings FEDTEST,

Cyber Hygiene scans of your host(s) conducted in the past day have detected one or both of the following:
* New critical and/or high vulnerabilities
* New potentially risky services

As part of BOD 19-02, critical findings need to be remediated within 15 days and high findings remediated within 30 days.

CISA also recommends reviewing hosts with potentially risky open services (e.g. RDP, Telnet, etc.) to ensure that each service is intended to be available to the public and, where applicable, the service is up-to-date on the latest version, correctly configured, and uses strong authentication.

The details are in the attached PDF, which has the same password as your Cyber Hygiene report.

If you have any questions, please contact our office.

Cheers,
CISA Cyber Assessments - Cyber Hygiene
Cybersecurity and Infrastructure Security Agency
vulnerability@cisa.dhs.gov

WARNING: This message and any attached document(s) is FOR OFFICIAL USE ONLY (FOUO). It contains information that may be exempt from public release under the Freedom of Information Act (5 U.S.G. 552). It is to be controlled, stored, handled, transmitted, distributed, and disposed of in accordance with DHS policy relating to FOUO information and is not to be released to the public or other personnel who do not have a valid "need-to-know" without prior approval of an authorized DHS official.
"""
                self.assertEqual(part.get_payload(), text_body)
            elif part.get_content_type() == "text/html":
                html_body = """<html>
<head></head>
<body>
<p>Greetings FEDTEST,</p>

<p>Cyber Hygiene scans of your host(s) conducted in the past day have detected one or both of the following:
<ul>
  <li>New critical and/or high vulnerabilities</li>
  <li>New potentially risky services</li>
</ul>
</p>

<p>As part of <a href="https://cyber.dhs.gov/bod/19-02/">BOD 19-02</a>, critical findings need to be remediated within 15 days and high findings remediated within 30 days.</p>

<p>CISA also recommends reviewing hosts with potentially risky open services (e.g. RDP, Telnet, etc.) to ensure that each service is intended to be available to the public and, where applicable, the service is up-to-date on the latest version, correctly configured, and uses strong authentication.</p>

<p>The details are in the attached PDF, which has the same password as your Cyber Hygiene report.</p>

<p>If you have any questions, please contact our office.</p>

<p>Cheers,<br>
CISA Cyber Assessments - Cyber Hygiene<br>
Cybersecurity and Infrastructure Security Agency<br>
<a href="mailto:vulnerability@cisa.dhs.gov">vulnerability@cisa.dhs.gov</a></p>

<p>WARNING: This message and any attached document(s) is FOR OFFICIAL USE ONLY (FOUO). It contains information that may be exempt from public release under the Freedom of Information Act (5 U.S.G. 552). It is to be controlled, stored, handled, transmitted, distributed, and disposed of in accordance with DHS policy relating to FOUO information and is not to be released to the public or other personnel who do not have a valid &ldquo;need-to-know&rdquo; without prior approval of an authorized DHS official.</p>
</body>
</html>
"""
                self.assertEqual(part.get_payload(), html_body)

    def test_four_params_multiple_recipients_fed(self):
        """Test the 4-parameter Federal version of the constructor."""
        to = ["recipient@example.com", "recipient2@example.com"]
        pdf = "./tests/data/pdf-sample.pdf"
        agency_acronym = "FEDTEST"
        is_federal = True
        report_date = "December 15, 2001"

        message = CyhyNotificationMessage(
            to, pdf, agency_acronym, is_federal, report_date
        )

        self.assertEqual(message["From"], "reports@cyber.dhs.gov")
        self.assertEqual(
            message["Subject"],
            "FEDTEST - Cyber Hygiene Alert - December 15, 2001",
        )
        self.assertEqual(message.get("CC"), None)
        self.assertEqual(message["BCC"], "cyhy_reports@hq.dhs.gov")
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
                body = """Greetings FEDTEST,

Cyber Hygiene scans of your host(s) conducted in the past day have detected one or both of the following:
* New critical and/or high vulnerabilities
* New potentially risky services

As part of BOD 19-02, critical findings need to be remediated within 15 days and high findings remediated within 30 days.

CISA also recommends reviewing hosts with potentially risky open services (e.g. RDP, Telnet, etc.) to ensure that each service is intended to be available to the public and, where applicable, the service is up-to-date on the latest version, correctly configured, and uses strong authentication.

The details are in the attached PDF, which has the same password as your Cyber Hygiene report.

If you have any questions, please contact our office.

Cheers,
CISA Cyber Assessments - Cyber Hygiene
Cybersecurity and Infrastructure Security Agency
vulnerability@cisa.dhs.gov

WARNING: This message and any attached document(s) is FOR OFFICIAL USE ONLY (FOUO). It contains information that may be exempt from public release under the Freedom of Information Act (5 U.S.G. 552). It is to be controlled, stored, handled, transmitted, distributed, and disposed of in accordance with DHS policy relating to FOUO information and is not to be released to the public or other personnel who do not have a valid "need-to-know" without prior approval of an authorized DHS official.
"""
                self.assertEqual(part.get_payload(), body)
            elif part.get_content_type() == "text/html":
                html_body = """<html>
<head></head>
<body>
<p>Greetings FEDTEST,</p>

<p>Cyber Hygiene scans of your host(s) conducted in the past day have detected one or both of the following:
<ul>
  <li>New critical and/or high vulnerabilities</li>
  <li>New potentially risky services</li>
</ul>
</p>

<p>As part of <a href="https://cyber.dhs.gov/bod/19-02/">BOD 19-02</a>, critical findings need to be remediated within 15 days and high findings remediated within 30 days.</p>

<p>CISA also recommends reviewing hosts with potentially risky open services (e.g. RDP, Telnet, etc.) to ensure that each service is intended to be available to the public and, where applicable, the service is up-to-date on the latest version, correctly configured, and uses strong authentication.</p>

<p>The details are in the attached PDF, which has the same password as your Cyber Hygiene report.</p>

<p>If you have any questions, please contact our office.</p>

<p>Cheers,<br>
CISA Cyber Assessments - Cyber Hygiene<br>
Cybersecurity and Infrastructure Security Agency<br>
<a href="mailto:vulnerability@cisa.dhs.gov">vulnerability@cisa.dhs.gov</a></p>

<p>WARNING: This message and any attached document(s) is FOR OFFICIAL USE ONLY (FOUO). It contains information that may be exempt from public release under the Freedom of Information Act (5 U.S.G. 552). It is to be controlled, stored, handled, transmitted, distributed, and disposed of in accordance with DHS policy relating to FOUO information and is not to be released to the public or other personnel who do not have a valid &ldquo;need-to-know&rdquo; without prior approval of an authorized DHS official.</p>
</body>
</html>
"""
                self.assertEqual(part.get_payload(), html_body)

    def test_six_params_single_cc_fed(self):
        """Test the 6-parameter Federal version of the constructor."""
        to = ["recipient@example.com", "recipient2@example.com"]
        pdf = "./tests/data/pdf-sample.pdf"
        fm = "sender@example.com"
        cc = ["cc@example.com"]
        bcc = ["bcc@example.com"]
        agency_acronym = "FEDTEST"
        is_federal = True
        report_date = "December 15, 2001"

        message = CyhyNotificationMessage(
            to,
            pdf,
            agency_acronym,
            is_federal,
            report_date,
            from_addr=fm,
            cc_addrs=cc,
            bcc_addrs=bcc,
        )

        self.assertEqual(message["From"], fm)
        self.assertEqual(
            message["Subject"],
            "FEDTEST - Cyber Hygiene Alert - December 15, 2001",
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
                body = """Greetings FEDTEST,

Cyber Hygiene scans of your host(s) conducted in the past day have detected one or both of the following:
* New critical and/or high vulnerabilities
* New potentially risky services

As part of BOD 19-02, critical findings need to be remediated within 15 days and high findings remediated within 30 days.

CISA also recommends reviewing hosts with potentially risky open services (e.g. RDP, Telnet, etc.) to ensure that each service is intended to be available to the public and, where applicable, the service is up-to-date on the latest version, correctly configured, and uses strong authentication.

The details are in the attached PDF, which has the same password as your Cyber Hygiene report.

If you have any questions, please contact our office.

Cheers,
CISA Cyber Assessments - Cyber Hygiene
Cybersecurity and Infrastructure Security Agency
vulnerability@cisa.dhs.gov

WARNING: This message and any attached document(s) is FOR OFFICIAL USE ONLY (FOUO). It contains information that may be exempt from public release under the Freedom of Information Act (5 U.S.G. 552). It is to be controlled, stored, handled, transmitted, distributed, and disposed of in accordance with DHS policy relating to FOUO information and is not to be released to the public or other personnel who do not have a valid "need-to-know" without prior approval of an authorized DHS official.
"""
                self.assertEqual(part.get_payload(), body)
            elif part.get_content_type() == "text/html":
                html_body = """<html>
<head></head>
<body>
<p>Greetings FEDTEST,</p>

<p>Cyber Hygiene scans of your host(s) conducted in the past day have detected one or both of the following:
<ul>
  <li>New critical and/or high vulnerabilities</li>
  <li>New potentially risky services</li>
</ul>
</p>

<p>As part of <a href="https://cyber.dhs.gov/bod/19-02/">BOD 19-02</a>, critical findings need to be remediated within 15 days and high findings remediated within 30 days.</p>

<p>CISA also recommends reviewing hosts with potentially risky open services (e.g. RDP, Telnet, etc.) to ensure that each service is intended to be available to the public and, where applicable, the service is up-to-date on the latest version, correctly configured, and uses strong authentication.</p>

<p>The details are in the attached PDF, which has the same password as your Cyber Hygiene report.</p>

<p>If you have any questions, please contact our office.</p>

<p>Cheers,<br>
CISA Cyber Assessments - Cyber Hygiene<br>
Cybersecurity and Infrastructure Security Agency<br>
<a href="mailto:vulnerability@cisa.dhs.gov">vulnerability@cisa.dhs.gov</a></p>

<p>WARNING: This message and any attached document(s) is FOR OFFICIAL USE ONLY (FOUO). It contains information that may be exempt from public release under the Freedom of Information Act (5 U.S.G. 552). It is to be controlled, stored, handled, transmitted, distributed, and disposed of in accordance with DHS policy relating to FOUO information and is not to be released to the public or other personnel who do not have a valid &ldquo;need-to-know&rdquo; without prior approval of an authorized DHS official.</p>
</body>
</html>
"""
                self.assertEqual(part.get_payload(), html_body)

    def test_six_params_multiple_cc_fed(self):
        """Test the 6-parameter Federal version of the constructor."""
        to = ["recipient@example.com", "recipient2@example.com"]
        pdf = "./tests/data/pdf-sample.pdf"
        fm = "sender@example.com"
        cc = ["cc@example.com", "cc2@example.com"]
        bcc = ["bcc@example.com", "bcc2@example.com"]
        agency_acronym = "FEDTEST"
        is_federal = True
        report_date = "December 15, 2001"

        message = CyhyNotificationMessage(
            to,
            pdf,
            agency_acronym,
            is_federal,
            report_date,
            from_addr=fm,
            cc_addrs=cc,
            bcc_addrs=bcc,
        )

        self.assertEqual(message["From"], fm)
        self.assertEqual(
            message["Subject"],
            "FEDTEST - Cyber Hygiene Alert - December 15, 2001",
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
                body = """Greetings FEDTEST,

Cyber Hygiene scans of your host(s) conducted in the past day have detected one or both of the following:
* New critical and/or high vulnerabilities
* New potentially risky services

As part of BOD 19-02, critical findings need to be remediated within 15 days and high findings remediated within 30 days.

CISA also recommends reviewing hosts with potentially risky open services (e.g. RDP, Telnet, etc.) to ensure that each service is intended to be available to the public and, where applicable, the service is up-to-date on the latest version, correctly configured, and uses strong authentication.

The details are in the attached PDF, which has the same password as your Cyber Hygiene report.

If you have any questions, please contact our office.

Cheers,
CISA Cyber Assessments - Cyber Hygiene
Cybersecurity and Infrastructure Security Agency
vulnerability@cisa.dhs.gov

WARNING: This message and any attached document(s) is FOR OFFICIAL USE ONLY (FOUO). It contains information that may be exempt from public release under the Freedom of Information Act (5 U.S.G. 552). It is to be controlled, stored, handled, transmitted, distributed, and disposed of in accordance with DHS policy relating to FOUO information and is not to be released to the public or other personnel who do not have a valid "need-to-know" without prior approval of an authorized DHS official.
"""
                self.assertEqual(part.get_payload(), body)
            elif part.get_content_type() == "text/html":
                html_body = """<html>
<head></head>
<body>
<p>Greetings FEDTEST,</p>

<p>Cyber Hygiene scans of your host(s) conducted in the past day have detected one or both of the following:
<ul>
  <li>New critical and/or high vulnerabilities</li>
  <li>New potentially risky services</li>
</ul>
</p>

<p>As part of <a href="https://cyber.dhs.gov/bod/19-02/">BOD 19-02</a>, critical findings need to be remediated within 15 days and high findings remediated within 30 days.</p>

<p>CISA also recommends reviewing hosts with potentially risky open services (e.g. RDP, Telnet, etc.) to ensure that each service is intended to be available to the public and, where applicable, the service is up-to-date on the latest version, correctly configured, and uses strong authentication.</p>

<p>The details are in the attached PDF, which has the same password as your Cyber Hygiene report.</p>

<p>If you have any questions, please contact our office.</p>

<p>Cheers,<br>
CISA Cyber Assessments - Cyber Hygiene<br>
Cybersecurity and Infrastructure Security Agency<br>
<a href="mailto:vulnerability@cisa.dhs.gov">vulnerability@cisa.dhs.gov</a></p>

<p>WARNING: This message and any attached document(s) is FOR OFFICIAL USE ONLY (FOUO). It contains information that may be exempt from public release under the Freedom of Information Act (5 U.S.G. 552). It is to be controlled, stored, handled, transmitted, distributed, and disposed of in accordance with DHS policy relating to FOUO information and is not to be released to the public or other personnel who do not have a valid &ldquo;need-to-know&rdquo; without prior approval of an authorized DHS official.</p>
</body>
</html>
"""
                self.assertEqual(part.get_payload(), html_body)

    def test_four_params_single_recipient_nonfed(self):
        """Test the 4-parameter non-Federal version of the constructor."""
        to = ["recipient@example.com"]
        pdf = "./tests/data/pdf-sample.pdf"
        agency_acronym = "NONFEDTEST"
        is_federal = False
        report_date = "December 15, 2001"

        message = CyhyNotificationMessage(
            to, pdf, agency_acronym, is_federal, report_date
        )

        self.assertEqual(message["From"], "reports@cyber.dhs.gov")
        self.assertEqual(
            message["Subject"],
            "NONFEDTEST - Cyber Hygiene Alert - December 15, 2001",
        )
        self.assertEqual(message.get("CC"), None)
        self.assertEqual(message["BCC"], "cyhy_reports@hq.dhs.gov")
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
                text_body = """Greetings NONFEDTEST,

Cyber Hygiene scans of your host(s) conducted in the past day have detected one or both of the following:
* New critical and/or high vulnerabilities
* New potentially risky services

CISA recommends remediating critical findings within 15 days and high findings within 30 days.

CISA also recommends reviewing hosts with potentially risky open services (e.g. RDP, Telnet, etc.) to ensure that each service is intended to be available to the public and, where applicable, the service is up-to-date on the latest version, correctly configured, and uses strong authentication.

The details are in the attached PDF, which has the same password as your Cyber Hygiene report.

If you have any questions, please contact our office.

Cheers,
CISA Cyber Assessments - Cyber Hygiene
Cybersecurity and Infrastructure Security Agency
vulnerability@cisa.dhs.gov

WARNING: This message and any attached document(s) is FOR OFFICIAL USE ONLY (FOUO). It contains information that may be exempt from public release under the Freedom of Information Act (5 U.S.G. 552). It is to be controlled, stored, handled, transmitted, distributed, and disposed of in accordance with DHS policy relating to FOUO information and is not to be released to the public or other personnel who do not have a valid "need-to-know" without prior approval of an authorized DHS official.
"""
                self.assertEqual(part.get_payload(), text_body)
            elif part.get_content_type() == "text/html":
                html_body = """<html>
<head></head>
<body>
<p>Greetings NONFEDTEST,</p>

<p>Cyber Hygiene scans of your host(s) conducted in the past day have detected one or both of the following:
<ul>
  <li>New critical and/or high vulnerabilities</li>
  <li>New potentially risky services</li>
</ul>
</p>

<p>CISA recommends remediating critical findings within 15 days and high findings within 30 days.</p>

<p>CISA also recommends reviewing hosts with potentially risky open services (e.g. RDP, Telnet, etc.) to ensure that each service is intended to be available to the public and, where applicable, the service is up-to-date on the latest version, correctly configured, and uses strong authentication.</p>

<p>The details are in the attached PDF, which has the same password as your Cyber Hygiene report.</p>

<p>If you have any questions, please contact our office.</p>

<p>Cheers,<br>
CISA Cyber Assessments - Cyber Hygiene<br>
Cybersecurity and Infrastructure Security Agency<br>
<a href="mailto:vulnerability@cisa.dhs.gov">vulnerability@cisa.dhs.gov</a></p>

<p>WARNING: This message and any attached document(s) is FOR OFFICIAL USE ONLY (FOUO). It contains information that may be exempt from public release under the Freedom of Information Act (5 U.S.G. 552). It is to be controlled, stored, handled, transmitted, distributed, and disposed of in accordance with DHS policy relating to FOUO information and is not to be released to the public or other personnel who do not have a valid &ldquo;need-to-know&rdquo; without prior approval of an authorized DHS official.</p>
</body>
</html>
"""
                self.assertEqual(part.get_payload(), html_body)

    def test_four_params_multiple_recipients_nonfed(self):
        """Test the 4-parameter non-Federal version of the constructor."""
        to = ["recipient@example.com", "recipient2@example.com"]
        pdf = "./tests/data/pdf-sample.pdf"
        agency_acronym = "NONFEDTEST"
        is_federal = False
        report_date = "December 15, 2001"

        message = CyhyNotificationMessage(
            to, pdf, agency_acronym, is_federal, report_date
        )

        self.assertEqual(message["From"], "reports@cyber.dhs.gov")
        self.assertEqual(
            message["Subject"],
            "NONFEDTEST - Cyber Hygiene Alert - December 15, 2001",
        )
        self.assertEqual(message.get("CC"), None)
        self.assertEqual(message["BCC"], "cyhy_reports@hq.dhs.gov")
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
                body = """Greetings NONFEDTEST,

Cyber Hygiene scans of your host(s) conducted in the past day have detected one or both of the following:
* New critical and/or high vulnerabilities
* New potentially risky services

CISA recommends remediating critical findings within 15 days and high findings within 30 days.

CISA also recommends reviewing hosts with potentially risky open services (e.g. RDP, Telnet, etc.) to ensure that each service is intended to be available to the public and, where applicable, the service is up-to-date on the latest version, correctly configured, and uses strong authentication.

The details are in the attached PDF, which has the same password as your Cyber Hygiene report.

If you have any questions, please contact our office.

Cheers,
CISA Cyber Assessments - Cyber Hygiene
Cybersecurity and Infrastructure Security Agency
vulnerability@cisa.dhs.gov

WARNING: This message and any attached document(s) is FOR OFFICIAL USE ONLY (FOUO). It contains information that may be exempt from public release under the Freedom of Information Act (5 U.S.G. 552). It is to be controlled, stored, handled, transmitted, distributed, and disposed of in accordance with DHS policy relating to FOUO information and is not to be released to the public or other personnel who do not have a valid "need-to-know" without prior approval of an authorized DHS official.
"""
                self.assertEqual(part.get_payload(), body)
            elif part.get_content_type() == "text/html":
                html_body = """<html>
<head></head>
<body>
<p>Greetings NONFEDTEST,</p>

<p>Cyber Hygiene scans of your host(s) conducted in the past day have detected one or both of the following:
<ul>
  <li>New critical and/or high vulnerabilities</li>
  <li>New potentially risky services</li>
</ul>
</p>

<p>CISA recommends remediating critical findings within 15 days and high findings within 30 days.</p>

<p>CISA also recommends reviewing hosts with potentially risky open services (e.g. RDP, Telnet, etc.) to ensure that each service is intended to be available to the public and, where applicable, the service is up-to-date on the latest version, correctly configured, and uses strong authentication.</p>

<p>The details are in the attached PDF, which has the same password as your Cyber Hygiene report.</p>

<p>If you have any questions, please contact our office.</p>

<p>Cheers,<br>
CISA Cyber Assessments - Cyber Hygiene<br>
Cybersecurity and Infrastructure Security Agency<br>
<a href="mailto:vulnerability@cisa.dhs.gov">vulnerability@cisa.dhs.gov</a></p>

<p>WARNING: This message and any attached document(s) is FOR OFFICIAL USE ONLY (FOUO). It contains information that may be exempt from public release under the Freedom of Information Act (5 U.S.G. 552). It is to be controlled, stored, handled, transmitted, distributed, and disposed of in accordance with DHS policy relating to FOUO information and is not to be released to the public or other personnel who do not have a valid &ldquo;need-to-know&rdquo; without prior approval of an authorized DHS official.</p>
</body>
</html>
"""
                self.assertEqual(part.get_payload(), html_body)

    def test_six_params_single_cc_nonfed(self):
        """Test the 6-parameter non-Federal version of the constructor."""
        to = ["recipient@example.com", "recipient2@example.com"]
        pdf = "./tests/data/pdf-sample.pdf"
        fm = "sender@example.com"
        cc = ["cc@example.com"]
        bcc = ["bcc@example.com"]
        agency_acronym = "NONFEDTEST"
        is_federal = False
        report_date = "December 15, 2001"

        message = CyhyNotificationMessage(
            to,
            pdf,
            agency_acronym,
            is_federal,
            report_date,
            from_addr=fm,
            cc_addrs=cc,
            bcc_addrs=bcc,
        )

        self.assertEqual(message["From"], fm)
        self.assertEqual(
            message["Subject"],
            "NONFEDTEST - Cyber Hygiene Alert - December 15, 2001",
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
                body = """Greetings NONFEDTEST,

Cyber Hygiene scans of your host(s) conducted in the past day have detected one or both of the following:
* New critical and/or high vulnerabilities
* New potentially risky services

CISA recommends remediating critical findings within 15 days and high findings within 30 days.

CISA also recommends reviewing hosts with potentially risky open services (e.g. RDP, Telnet, etc.) to ensure that each service is intended to be available to the public and, where applicable, the service is up-to-date on the latest version, correctly configured, and uses strong authentication.

The details are in the attached PDF, which has the same password as your Cyber Hygiene report.

If you have any questions, please contact our office.

Cheers,
CISA Cyber Assessments - Cyber Hygiene
Cybersecurity and Infrastructure Security Agency
vulnerability@cisa.dhs.gov

WARNING: This message and any attached document(s) is FOR OFFICIAL USE ONLY (FOUO). It contains information that may be exempt from public release under the Freedom of Information Act (5 U.S.G. 552). It is to be controlled, stored, handled, transmitted, distributed, and disposed of in accordance with DHS policy relating to FOUO information and is not to be released to the public or other personnel who do not have a valid "need-to-know" without prior approval of an authorized DHS official.
"""
                self.assertEqual(part.get_payload(), body)
            elif part.get_content_type() == "text/html":
                html_body = """<html>
<head></head>
<body>
<p>Greetings NONFEDTEST,</p>

<p>Cyber Hygiene scans of your host(s) conducted in the past day have detected one or both of the following:
<ul>
  <li>New critical and/or high vulnerabilities</li>
  <li>New potentially risky services</li>
</ul>
</p>

<p>CISA recommends remediating critical findings within 15 days and high findings within 30 days.</p>

<p>CISA also recommends reviewing hosts with potentially risky open services (e.g. RDP, Telnet, etc.) to ensure that each service is intended to be available to the public and, where applicable, the service is up-to-date on the latest version, correctly configured, and uses strong authentication.</p>

<p>The details are in the attached PDF, which has the same password as your Cyber Hygiene report.</p>

<p>If you have any questions, please contact our office.</p>

<p>Cheers,<br>
CISA Cyber Assessments - Cyber Hygiene<br>
Cybersecurity and Infrastructure Security Agency<br>
<a href="mailto:vulnerability@cisa.dhs.gov">vulnerability@cisa.dhs.gov</a></p>

<p>WARNING: This message and any attached document(s) is FOR OFFICIAL USE ONLY (FOUO). It contains information that may be exempt from public release under the Freedom of Information Act (5 U.S.G. 552). It is to be controlled, stored, handled, transmitted, distributed, and disposed of in accordance with DHS policy relating to FOUO information and is not to be released to the public or other personnel who do not have a valid &ldquo;need-to-know&rdquo; without prior approval of an authorized DHS official.</p>
</body>
</html>
"""
                self.assertEqual(part.get_payload(), html_body)

    def test_six_params_multiple_cc_nonfed(self):
        """Test the 6-parameter non-Federal version of the constructor."""
        to = ["recipient@example.com", "recipient2@example.com"]
        pdf = "./tests/data/pdf-sample.pdf"
        fm = "sender@example.com"
        cc = ["cc@example.com", "cc2@example.com"]
        bcc = ["bcc@example.com", "bcc2@example.com"]
        agency_acronym = "NONFEDTEST"
        is_federal = False
        report_date = "December 15, 2001"

        message = CyhyNotificationMessage(
            to,
            pdf,
            agency_acronym,
            is_federal,
            report_date,
            from_addr=fm,
            cc_addrs=cc,
            bcc_addrs=bcc,
        )

        self.assertEqual(message["From"], fm)
        self.assertEqual(
            message["Subject"],
            "NONFEDTEST - Cyber Hygiene Alert - December 15, 2001",
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
                body = """Greetings NONFEDTEST,

Cyber Hygiene scans of your host(s) conducted in the past day have detected one or both of the following:
* New critical and/or high vulnerabilities
* New potentially risky services

CISA recommends remediating critical findings within 15 days and high findings within 30 days.

CISA also recommends reviewing hosts with potentially risky open services (e.g. RDP, Telnet, etc.) to ensure that each service is intended to be available to the public and, where applicable, the service is up-to-date on the latest version, correctly configured, and uses strong authentication.

The details are in the attached PDF, which has the same password as your Cyber Hygiene report.

If you have any questions, please contact our office.

Cheers,
CISA Cyber Assessments - Cyber Hygiene
Cybersecurity and Infrastructure Security Agency
vulnerability@cisa.dhs.gov

WARNING: This message and any attached document(s) is FOR OFFICIAL USE ONLY (FOUO). It contains information that may be exempt from public release under the Freedom of Information Act (5 U.S.G. 552). It is to be controlled, stored, handled, transmitted, distributed, and disposed of in accordance with DHS policy relating to FOUO information and is not to be released to the public or other personnel who do not have a valid "need-to-know" without prior approval of an authorized DHS official.
"""
                self.assertEqual(part.get_payload(), body)
            elif part.get_content_type() == "text/html":
                html_body = """<html>
<head></head>
<body>
<p>Greetings NONFEDTEST,</p>

<p>Cyber Hygiene scans of your host(s) conducted in the past day have detected one or both of the following:
<ul>
  <li>New critical and/or high vulnerabilities</li>
  <li>New potentially risky services</li>
</ul>
</p>

<p>CISA recommends remediating critical findings within 15 days and high findings within 30 days.</p>

<p>CISA also recommends reviewing hosts with potentially risky open services (e.g. RDP, Telnet, etc.) to ensure that each service is intended to be available to the public and, where applicable, the service is up-to-date on the latest version, correctly configured, and uses strong authentication.</p>

<p>The details are in the attached PDF, which has the same password as your Cyber Hygiene report.</p>

<p>If you have any questions, please contact our office.</p>

<p>Cheers,<br>
CISA Cyber Assessments - Cyber Hygiene<br>
Cybersecurity and Infrastructure Security Agency<br>
<a href="mailto:vulnerability@cisa.dhs.gov">vulnerability@cisa.dhs.gov</a></p>

<p>WARNING: This message and any attached document(s) is FOR OFFICIAL USE ONLY (FOUO). It contains information that may be exempt from public release under the Freedom of Information Act (5 U.S.G. 552). It is to be controlled, stored, handled, transmitted, distributed, and disposed of in accordance with DHS policy relating to FOUO information and is not to be released to the public or other personnel who do not have a valid &ldquo;need-to-know&rdquo; without prior approval of an authorized DHS official.</p>
</body>
</html>
"""
                self.assertEqual(part.get_payload(), html_body)


if __name__ == "__main__":
    unittest.main()
