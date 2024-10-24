"""This module contains the tests for the CyhyNotificationMessage class."""

# Standard Python Libraries
import unittest

# cisagov Libraries
from cyhy.mailer.CyhyNotificationMessage import CyhyNotificationMessage


class Test(unittest.TestCase):
    """The tests for the CyhyNotificationMessage class."""

    def test_four_params_single_recipient_fed(self):
        """Test the 4-parameter Federal version of the constructor."""
        to = ["recipient@example.com"]
        pdf = "./tests/data/pdf-sample.pdf"
        entity_acronym = "FEDTEST"
        entity_name = "Federal Test"
        is_federal = True
        report_date = "December 15, 2001"

        message = CyhyNotificationMessage(
            to, pdf, entity_acronym, entity_name, is_federal, report_date
        )

        self.assertEqual(message["From"], "reports@cyber.dhs.gov")
        self.assertEqual(
            message["Subject"],
            "FEDTEST - Cyber Hygiene Alert - December 15, 2001",
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
                text_body = """Greetings Federal Test (FEDTEST),

Cyber Hygiene scans of your host(s) conducted in the past day have detected one or more of the following:
* New critical, high, and/or known exploited vulnerabilities
* New potentially risky services

As part of BOD 19-02, critical findings need to be remediated within 15 days and high findings remediated within 30 days.

As part of BOD 22-01, any "known exploited" findings, regardless of severity, need to be remediated within two weeks.

CISA also recommends reviewing hosts with potentially risky open services (e.g. RDP, Telnet, etc.), especially if they are functioning as networked management interfaces, to ensure that each service is intended to be available to the public and, where applicable, the service is up-to-date, correctly configured, and uses strong authentication.

As part of BOD 23-02, networked management interfaces exposed to the public internet must either be removed from the internet by making it only accessible from an internal enterprise network or protected by capabilities that enforce access control to the interface through a policy enforcement point separate from the interface itself as part of a Zero Trust Architecture within 14 days.

The details are in the attached PDF, which has the same password as your weekly Cyber Hygiene Vulnerability Scanning report.

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
<p>Greetings Federal Test (FEDTEST),</p>

<p>Cyber Hygiene scans of your host(s) conducted in the past day have detected one or more of the following:
<ul>
  <li>New critical, high, and/or known exploited vulnerabilities</li>
  <li>New potentially risky services</li>
</ul>
</p>

<p>As part of <a href="https://www.cisa.gov/news-events/directives/bod-19-02-vulnerability-remediation-requirements-internet-accessible-systems">BOD 19-02</a>, critical findings need to be remediated within 15 days and high findings remediated within 30 days.</p>

<p>As part of <a href="https://www.cisa.gov/news-events/directives/bod-22-01-reducing-significant-risk-known-exploited-vulnerabilities">BOD 22-01</a>, any "known exploited" findings, regardless of severity, need to be remediated within two weeks.</p>

<p>CISA also recommends reviewing hosts with potentially risky open services (e.g. RDP, Telnet, etc.), <em>especially if they are functioning as networked management interfaces</em>, to ensure that each service is intended to be available to the public and, where applicable, the service is up-to-date, correctly configured, and uses strong authentication.</p>

<p>As part of <a href="https://www.cisa.gov/news-events/directives/binding-operational-directive-23-02">BOD 23-02</a>, networked management interfaces exposed to the public internet must either be removed from the internet by making it only accessible from an internal enterprise network or protected by capabilities that enforce access control to the interface through a policy enforcement point separate from the interface itself as part of a Zero Trust Architecture within 14 days.</p>

<p>The details are in the attached PDF, which has the same password as your weekly Cyber Hygiene Vulnerability Scanning report.</p>

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
        entity_acronym = "FEDTEST"
        entity_name = "Federal Test"
        is_federal = True
        report_date = "December 15, 2001"

        message = CyhyNotificationMessage(
            to, pdf, entity_acronym, entity_name, is_federal, report_date
        )

        self.assertEqual(message["From"], "reports@cyber.dhs.gov")
        self.assertEqual(
            message["Subject"],
            "FEDTEST - Cyber Hygiene Alert - December 15, 2001",
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
                body = """Greetings Federal Test (FEDTEST),

Cyber Hygiene scans of your host(s) conducted in the past day have detected one or more of the following:
* New critical, high, and/or known exploited vulnerabilities
* New potentially risky services

As part of BOD 19-02, critical findings need to be remediated within 15 days and high findings remediated within 30 days.

As part of BOD 22-01, any "known exploited" findings, regardless of severity, need to be remediated within two weeks.

CISA also recommends reviewing hosts with potentially risky open services (e.g. RDP, Telnet, etc.), especially if they are functioning as networked management interfaces, to ensure that each service is intended to be available to the public and, where applicable, the service is up-to-date, correctly configured, and uses strong authentication.

As part of BOD 23-02, networked management interfaces exposed to the public internet must either be removed from the internet by making it only accessible from an internal enterprise network or protected by capabilities that enforce access control to the interface through a policy enforcement point separate from the interface itself as part of a Zero Trust Architecture within 14 days.

The details are in the attached PDF, which has the same password as your weekly Cyber Hygiene Vulnerability Scanning report.

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
<p>Greetings Federal Test (FEDTEST),</p>

<p>Cyber Hygiene scans of your host(s) conducted in the past day have detected one or more of the following:
<ul>
  <li>New critical, high, and/or known exploited vulnerabilities</li>
  <li>New potentially risky services</li>
</ul>
</p>

<p>As part of <a href="https://www.cisa.gov/news-events/directives/bod-19-02-vulnerability-remediation-requirements-internet-accessible-systems">BOD 19-02</a>, critical findings need to be remediated within 15 days and high findings remediated within 30 days.</p>

<p>As part of <a href="https://www.cisa.gov/news-events/directives/bod-22-01-reducing-significant-risk-known-exploited-vulnerabilities">BOD 22-01</a>, any "known exploited" findings, regardless of severity, need to be remediated within two weeks.</p>

<p>CISA also recommends reviewing hosts with potentially risky open services (e.g. RDP, Telnet, etc.), <em>especially if they are functioning as networked management interfaces</em>, to ensure that each service is intended to be available to the public and, where applicable, the service is up-to-date, correctly configured, and uses strong authentication.</p>

<p>As part of <a href="https://www.cisa.gov/news-events/directives/binding-operational-directive-23-02">BOD 23-02</a>, networked management interfaces exposed to the public internet must either be removed from the internet by making it only accessible from an internal enterprise network or protected by capabilities that enforce access control to the interface through a policy enforcement point separate from the interface itself as part of a Zero Trust Architecture within 14 days.</p>

<p>The details are in the attached PDF, which has the same password as your weekly Cyber Hygiene Vulnerability Scanning report.</p>

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
        entity_acronym = "FEDTEST"
        entity_name = "Federal Test"
        is_federal = True
        report_date = "December 15, 2001"

        message = CyhyNotificationMessage(
            to,
            pdf,
            entity_acronym,
            entity_name,
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
                body = """Greetings Federal Test (FEDTEST),

Cyber Hygiene scans of your host(s) conducted in the past day have detected one or more of the following:
* New critical, high, and/or known exploited vulnerabilities
* New potentially risky services

As part of BOD 19-02, critical findings need to be remediated within 15 days and high findings remediated within 30 days.

As part of BOD 22-01, any "known exploited" findings, regardless of severity, need to be remediated within two weeks.

CISA also recommends reviewing hosts with potentially risky open services (e.g. RDP, Telnet, etc.), especially if they are functioning as networked management interfaces, to ensure that each service is intended to be available to the public and, where applicable, the service is up-to-date, correctly configured, and uses strong authentication.

As part of BOD 23-02, networked management interfaces exposed to the public internet must either be removed from the internet by making it only accessible from an internal enterprise network or protected by capabilities that enforce access control to the interface through a policy enforcement point separate from the interface itself as part of a Zero Trust Architecture within 14 days.

The details are in the attached PDF, which has the same password as your weekly Cyber Hygiene Vulnerability Scanning report.

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
<p>Greetings Federal Test (FEDTEST),</p>

<p>Cyber Hygiene scans of your host(s) conducted in the past day have detected one or more of the following:
<ul>
  <li>New critical, high, and/or known exploited vulnerabilities</li>
  <li>New potentially risky services</li>
</ul>
</p>

<p>As part of <a href="https://www.cisa.gov/news-events/directives/bod-19-02-vulnerability-remediation-requirements-internet-accessible-systems">BOD 19-02</a>, critical findings need to be remediated within 15 days and high findings remediated within 30 days.</p>

<p>As part of <a href="https://www.cisa.gov/news-events/directives/bod-22-01-reducing-significant-risk-known-exploited-vulnerabilities">BOD 22-01</a>, any "known exploited" findings, regardless of severity, need to be remediated within two weeks.</p>

<p>CISA also recommends reviewing hosts with potentially risky open services (e.g. RDP, Telnet, etc.), <em>especially if they are functioning as networked management interfaces</em>, to ensure that each service is intended to be available to the public and, where applicable, the service is up-to-date, correctly configured, and uses strong authentication.</p>

<p>As part of <a href="https://www.cisa.gov/news-events/directives/binding-operational-directive-23-02">BOD 23-02</a>, networked management interfaces exposed to the public internet must either be removed from the internet by making it only accessible from an internal enterprise network or protected by capabilities that enforce access control to the interface through a policy enforcement point separate from the interface itself as part of a Zero Trust Architecture within 14 days.</p>

<p>The details are in the attached PDF, which has the same password as your weekly Cyber Hygiene Vulnerability Scanning report.</p>

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
        entity_acronym = "FEDTEST"
        entity_name = "Federal Test"
        is_federal = True
        report_date = "December 15, 2001"

        message = CyhyNotificationMessage(
            to,
            pdf,
            entity_acronym,
            entity_name,
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
                body = """Greetings Federal Test (FEDTEST),

Cyber Hygiene scans of your host(s) conducted in the past day have detected one or more of the following:
* New critical, high, and/or known exploited vulnerabilities
* New potentially risky services

As part of BOD 19-02, critical findings need to be remediated within 15 days and high findings remediated within 30 days.

As part of BOD 22-01, any "known exploited" findings, regardless of severity, need to be remediated within two weeks.

CISA also recommends reviewing hosts with potentially risky open services (e.g. RDP, Telnet, etc.), especially if they are functioning as networked management interfaces, to ensure that each service is intended to be available to the public and, where applicable, the service is up-to-date, correctly configured, and uses strong authentication.

As part of BOD 23-02, networked management interfaces exposed to the public internet must either be removed from the internet by making it only accessible from an internal enterprise network or protected by capabilities that enforce access control to the interface through a policy enforcement point separate from the interface itself as part of a Zero Trust Architecture within 14 days.

The details are in the attached PDF, which has the same password as your weekly Cyber Hygiene Vulnerability Scanning report.

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
<p>Greetings Federal Test (FEDTEST),</p>

<p>Cyber Hygiene scans of your host(s) conducted in the past day have detected one or more of the following:
<ul>
  <li>New critical, high, and/or known exploited vulnerabilities</li>
  <li>New potentially risky services</li>
</ul>
</p>

<p>As part of <a href="https://www.cisa.gov/news-events/directives/bod-19-02-vulnerability-remediation-requirements-internet-accessible-systems">BOD 19-02</a>, critical findings need to be remediated within 15 days and high findings remediated within 30 days.</p>

<p>As part of <a href="https://www.cisa.gov/news-events/directives/bod-22-01-reducing-significant-risk-known-exploited-vulnerabilities">BOD 22-01</a>, any "known exploited" findings, regardless of severity, need to be remediated within two weeks.</p>

<p>CISA also recommends reviewing hosts with potentially risky open services (e.g. RDP, Telnet, etc.), <em>especially if they are functioning as networked management interfaces</em>, to ensure that each service is intended to be available to the public and, where applicable, the service is up-to-date, correctly configured, and uses strong authentication.</p>

<p>As part of <a href="https://www.cisa.gov/news-events/directives/binding-operational-directive-23-02">BOD 23-02</a>, networked management interfaces exposed to the public internet must either be removed from the internet by making it only accessible from an internal enterprise network or protected by capabilities that enforce access control to the interface through a policy enforcement point separate from the interface itself as part of a Zero Trust Architecture within 14 days.</p>

<p>The details are in the attached PDF, which has the same password as your weekly Cyber Hygiene Vulnerability Scanning report.</p>

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
        entity_acronym = "NONFEDTEST"
        entity_name = "Non-Federal Test"
        is_federal = False
        report_date = "December 15, 2001"

        message = CyhyNotificationMessage(
            to, pdf, entity_acronym, entity_name, is_federal, report_date
        )

        self.assertEqual(message["From"], "reports@cyber.dhs.gov")
        self.assertEqual(
            message["Subject"],
            "NONFEDTEST - Cyber Hygiene Alert - December 15, 2001",
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
                text_body = """Greetings Non-Federal Test (NONFEDTEST),

Cyber Hygiene scans of your host(s) conducted in the past day have detected one or more of the following:
* New critical, high, and/or known exploited vulnerabilities
* New potentially risky services

CISA recommends remediating critical findings within 15 days and high findings within 30 days.

CISA recommends remediating known exploited vulnerabilities, regardless of severity, within two weeks.

CISA also recommends reviewing hosts with potentially risky open services (e.g. RDP, Telnet, etc.), especially if they are functioning as networked management interfaces, to ensure that each service is intended to be available to the public and, where applicable, the service is up-to-date, correctly configured, and uses strong authentication.



The details are in the attached PDF, which has the same password as your weekly Cyber Hygiene Vulnerability Scanning report.

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
<p>Greetings Non-Federal Test (NONFEDTEST),</p>

<p>Cyber Hygiene scans of your host(s) conducted in the past day have detected one or more of the following:
<ul>
  <li>New critical, high, and/or known exploited vulnerabilities</li>
  <li>New potentially risky services</li>
</ul>
</p>

<p>CISA recommends remediating critical findings within 15 days and high findings within 30 days.</p>

<p>CISA recommends remediating known exploited vulnerabilities, regardless of severity, within two weeks.</p>

<p>CISA also recommends reviewing hosts with potentially risky open services (e.g. RDP, Telnet, etc.), <em>especially if they are functioning as networked management interfaces</em>, to ensure that each service is intended to be available to the public and, where applicable, the service is up-to-date, correctly configured, and uses strong authentication.</p>

<p></p>

<p>The details are in the attached PDF, which has the same password as your weekly Cyber Hygiene Vulnerability Scanning report.</p>

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
        entity_acronym = "NONFEDTEST"
        entity_name = "Non-Federal Test"
        is_federal = False
        report_date = "December 15, 2001"

        message = CyhyNotificationMessage(
            to, pdf, entity_acronym, entity_name, is_federal, report_date
        )

        self.assertEqual(message["From"], "reports@cyber.dhs.gov")
        self.assertEqual(
            message["Subject"],
            "NONFEDTEST - Cyber Hygiene Alert - December 15, 2001",
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
                body = """Greetings Non-Federal Test (NONFEDTEST),

Cyber Hygiene scans of your host(s) conducted in the past day have detected one or more of the following:
* New critical, high, and/or known exploited vulnerabilities
* New potentially risky services

CISA recommends remediating critical findings within 15 days and high findings within 30 days.

CISA recommends remediating known exploited vulnerabilities, regardless of severity, within two weeks.

CISA also recommends reviewing hosts with potentially risky open services (e.g. RDP, Telnet, etc.), especially if they are functioning as networked management interfaces, to ensure that each service is intended to be available to the public and, where applicable, the service is up-to-date, correctly configured, and uses strong authentication.



The details are in the attached PDF, which has the same password as your weekly Cyber Hygiene Vulnerability Scanning report.

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
<p>Greetings Non-Federal Test (NONFEDTEST),</p>

<p>Cyber Hygiene scans of your host(s) conducted in the past day have detected one or more of the following:
<ul>
  <li>New critical, high, and/or known exploited vulnerabilities</li>
  <li>New potentially risky services</li>
</ul>
</p>

<p>CISA recommends remediating critical findings within 15 days and high findings within 30 days.</p>

<p>CISA recommends remediating known exploited vulnerabilities, regardless of severity, within two weeks.</p>

<p>CISA also recommends reviewing hosts with potentially risky open services (e.g. RDP, Telnet, etc.), <em>especially if they are functioning as networked management interfaces</em>, to ensure that each service is intended to be available to the public and, where applicable, the service is up-to-date, correctly configured, and uses strong authentication.</p>

<p></p>

<p>The details are in the attached PDF, which has the same password as your weekly Cyber Hygiene Vulnerability Scanning report.</p>

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
        entity_acronym = "NONFEDTEST"
        entity_name = "Non-Federal Test"
        is_federal = False
        report_date = "December 15, 2001"

        message = CyhyNotificationMessage(
            to,
            pdf,
            entity_acronym,
            entity_name,
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
                body = """Greetings Non-Federal Test (NONFEDTEST),

Cyber Hygiene scans of your host(s) conducted in the past day have detected one or more of the following:
* New critical, high, and/or known exploited vulnerabilities
* New potentially risky services

CISA recommends remediating critical findings within 15 days and high findings within 30 days.

CISA recommends remediating known exploited vulnerabilities, regardless of severity, within two weeks.

CISA also recommends reviewing hosts with potentially risky open services (e.g. RDP, Telnet, etc.), especially if they are functioning as networked management interfaces, to ensure that each service is intended to be available to the public and, where applicable, the service is up-to-date, correctly configured, and uses strong authentication.



The details are in the attached PDF, which has the same password as your weekly Cyber Hygiene Vulnerability Scanning report.

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
<p>Greetings Non-Federal Test (NONFEDTEST),</p>

<p>Cyber Hygiene scans of your host(s) conducted in the past day have detected one or more of the following:
<ul>
  <li>New critical, high, and/or known exploited vulnerabilities</li>
  <li>New potentially risky services</li>
</ul>
</p>

<p>CISA recommends remediating critical findings within 15 days and high findings within 30 days.</p>

<p>CISA recommends remediating known exploited vulnerabilities, regardless of severity, within two weeks.</p>

<p>CISA also recommends reviewing hosts with potentially risky open services (e.g. RDP, Telnet, etc.), <em>especially if they are functioning as networked management interfaces</em>, to ensure that each service is intended to be available to the public and, where applicable, the service is up-to-date, correctly configured, and uses strong authentication.</p>

<p></p>

<p>The details are in the attached PDF, which has the same password as your weekly Cyber Hygiene Vulnerability Scanning report.</p>

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
        entity_acronym = "NONFEDTEST"
        entity_name = "Non-Federal Test"
        is_federal = False
        report_date = "December 15, 2001"

        message = CyhyNotificationMessage(
            to,
            pdf,
            entity_acronym,
            entity_name,
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
                body = """Greetings Non-Federal Test (NONFEDTEST),

Cyber Hygiene scans of your host(s) conducted in the past day have detected one or more of the following:
* New critical, high, and/or known exploited vulnerabilities
* New potentially risky services

CISA recommends remediating critical findings within 15 days and high findings within 30 days.

CISA recommends remediating known exploited vulnerabilities, regardless of severity, within two weeks.

CISA also recommends reviewing hosts with potentially risky open services (e.g. RDP, Telnet, etc.), especially if they are functioning as networked management interfaces, to ensure that each service is intended to be available to the public and, where applicable, the service is up-to-date, correctly configured, and uses strong authentication.



The details are in the attached PDF, which has the same password as your weekly Cyber Hygiene Vulnerability Scanning report.

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
<p>Greetings Non-Federal Test (NONFEDTEST),</p>

<p>Cyber Hygiene scans of your host(s) conducted in the past day have detected one or more of the following:
<ul>
  <li>New critical, high, and/or known exploited vulnerabilities</li>
  <li>New potentially risky services</li>
</ul>
</p>

<p>CISA recommends remediating critical findings within 15 days and high findings within 30 days.</p>

<p>CISA recommends remediating known exploited vulnerabilities, regardless of severity, within two weeks.</p>

<p>CISA also recommends reviewing hosts with potentially risky open services (e.g. RDP, Telnet, etc.), <em>especially if they are functioning as networked management interfaces</em>, to ensure that each service is intended to be available to the public and, where applicable, the service is up-to-date, correctly configured, and uses strong authentication.</p>

<p></p>

<p>The details are in the attached PDF, which has the same password as your weekly Cyber Hygiene Vulnerability Scanning report.</p>

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
