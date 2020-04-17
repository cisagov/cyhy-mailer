"""This module contains the tests for the TmailMessage class."""

import unittest

from cyhy.mailer.TmailMessage import TmailMessage


class Test(unittest.TestCase):
    """The tests for the TmailMessage class."""

    def test_four_params_single_recipient(self):
        """Test the 4-parameter version of the constructor."""
        to = ["recipient@example.com"]
        pdf = "./tests/data/pdf-sample.pdf"
        agency_acronym = "CLARKE"
        report_date = "December 15, 2001"

        message = TmailMessage(to, pdf, agency_acronym, report_date)

        self.assertEqual(message["From"], "reports@cyber.dhs.gov")
        self.assertEqual(
            message["Subject"],
            "CLARKE - Trustworthy Email Report - December 15, 2001 Results",
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
                text_body = """Greetings CLARKE,

Attached is your Trustworthy Email Report. This report presents your organization's support of SPF and DMARC, two email authentication standards, as published at your .gov domains. The data in this report comes from a scan that took place on December 15, 2001.

CISA Binding Operational Directive 18-01 requires your agency to take certain actions relevant to the data in this report:
* Within 90 days of BOD issuance, configure all second-level domains to have valid SPF/DMARC records, with at minimum a DMARC policy of "p=none" and at least one address defined as a recipient of aggregate and/or failure reports.
* Within one year of BOD issuance, set a DMARC policy of "reject" for all second-level domains and mail-sending hosts.
* The Directive additionally requires all internet-facing mail servers to offer STARTTLS. This data will be represented in the Trustworthy Email Report in December.

Raw results in this Report are available as a CSV in the Appendix, which includes error messages. Note that this report includes data from second-level .gov domains, but the Directive's scope includes any domain suffix.

The actions the Directive requires increase the security of emails in transit and makes it easier to detect emails that attempt to spoof .gov domains. This protects intra-government users and the general public equally. See https://cyber.dhs.gov/bod/18-01/#introduction-to-email-authentication for more information about email authentication, as well as https://cyber.dhs.gov/bod/18-01/#compliance-guide and https://cyber.dhs.gov/bod/18-01/#frequently-asked-questions for a compliance guide and FAQ, respectively.

If you believe our reporting or methodology is in error, let us know. If the flaw appears tool-related, we encourage you to file an issue on our open-source scanner at https://github.com/cisagov/trustymail.

We welcome your feedback and questions.

Cheers,
The NCATS Team

National Cybersecurity Assessments and Technical Services (NCATS)
Cybersecurity and Infrastructure Security Agency (CISA)
vulnerability@cisa.dhs.gov

----changelog----
12/11/2017
* Known issue: The fed.us TLD is inaccurately represented in some reports.
03/29/2019
* If an SMTP-responsive hostname does not have an SPF record set, but it is covered by a valid DMARC record with a policy of reject, we now count the hostname as compliant with respect to SPF.  This change is being made to more closely align with the exact language in BOD 18-01.  As a result, users may see an increase in SPF record compliance scores.
-----------------
"""
                self.assertEqual(part.get_payload(), text_body)
            elif part.get_content_type() == "text/html":
                html_body = """<html>
<head></head>
<body>
<div style=""font-size:14.5"">
<p>Greetings CLARKE,</p>
<p>Attached is your <b>Trustworthy Email Report</b>. This report presents your organization's support of SPF and DMARC, two email authentication standards, as published at your .gov domains. The data in this report comes from a <b>scan that took place on December 15, 2001.</b></p>
<p><a href="https://cyber.dhs.gov/bod/18-01/">CISA Binding Operational Directive 18-01</a> requires your agency to take certain actions relevant to the data in this report:</p>
<ul>
<li>Within 90 days of BOD issuance, configure all second-level domains to have valid SPF/DMARC records, with at minimum a DMARC policy of &ldquo;p=none&rdquo; and at least one address defined as a recipient of aggregate and/or failure reports.</li>
<li>Within one year of BOD issuance, set a DMARC policy of &ldquo;reject&rdquo; for all second-level domains and mail-sending hosts.</li>
<li>(The Directive additionally requires all internet-facing mail servers to offer STARTTLS. This data will be represented in the Trustworthy Email Report in December.</li>
</ul>
</p>
<p>Raw results in this Report are available as a CSV in the Appendix, which includes error messages. Note that this report includes data from second-level .gov domains, but the Directive's <a href="https://cyber.dhs.gov/bod/18-01/#what-is-the-scope-of-bod-18-01">scope includes any domain suffix</a>.</p>
<p>The actions the Directive requires increases the security of emails in transit and makes it easier to detect emails that attempt to spoof .gov domains. This protects intra-government users and the general public equally. See <a href="https://cyber.dhs.gov/bod/18-01/#introduction-to-email-authentication">cyber.dhs.gov/bod/18-01/#introduction-to-email-authentication</a> for more information about email authentication, as well as <a href="https://cyber.dhs.gov/bod/18-01/#compliance-guide">cyber.dhs.gov/bod/18-01/#compliance-guide</a> and <a href="https://cyber.dhs.gov/bod/18-01/#frequently-asked-questions">cyber.dhs.gov/bod/18-01/#frequently-asked-questions</a> for a compliance guide and FAQ, respectively.</p>
<p>If you believe our reporting or methodology is in error, let us know. If the flaw appears tool-related, we encourage you to <a href="https://github.com/cisagov/trustymail">file an issue</a> on our open-source scanner.</p>
<p>We welcome your feedback and questions.</p>
Cheers,<br>
The NCATS Team<br><br />
National Cybersecurity Assessments and Technical Services (NCATS)<br />
Cybersecurity and Infrastructure Security Agency (CISA)<br />
<a href=""mailto:vulnerability@cisa.dhs.gov"">vulnerability@cisa.dhs.gov</a></p>
</div></p><br>
<p>----changelog----</p>
<p><i>12/11/2017</i></p>
<b>* Known issue:</b> The fed.us TLD is inaccurately represented in some reports.</p>
<p><i>03/29/2019</i></p>
<b>* </b> If an SMTP-responsive hostname does not have an SPF record set, but it is covered by a valid DMARC record with a policy of reject, we now count the hostname as compliant with respect to SPF.  This change is being made to more closely align with the exact language in BOD 18-01.  As a result, users may see an increase in SPF record compliance scores. </p>
<p>--------------------</p>
</body>
</html>
"""
                self.assertEqual(part.get_payload(), html_body)

    def test_four_params_multiple_recipients(self):
        """Test the 4-parameter version of the constructor."""
        to = ["recipient@example.com", "recipient2@example.com"]
        pdf = "./tests/data/pdf-sample.pdf"
        agency_acronym = "CLARKE"
        report_date = "December 15, 2001"

        message = TmailMessage(to, pdf, agency_acronym, report_date)

        self.assertEqual(message["From"], "reports@cyber.dhs.gov")
        self.assertEqual(
            message["Subject"],
            "CLARKE - Trustworthy Email Report - December 15, 2001 Results",
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
                body = """Greetings CLARKE,

Attached is your Trustworthy Email Report. This report presents your organization's support of SPF and DMARC, two email authentication standards, as published at your .gov domains. The data in this report comes from a scan that took place on December 15, 2001.

CISA Binding Operational Directive 18-01 requires your agency to take certain actions relevant to the data in this report:
* Within 90 days of BOD issuance, configure all second-level domains to have valid SPF/DMARC records, with at minimum a DMARC policy of "p=none" and at least one address defined as a recipient of aggregate and/or failure reports.
* Within one year of BOD issuance, set a DMARC policy of "reject" for all second-level domains and mail-sending hosts.
* The Directive additionally requires all internet-facing mail servers to offer STARTTLS. This data will be represented in the Trustworthy Email Report in December.

Raw results in this Report are available as a CSV in the Appendix, which includes error messages. Note that this report includes data from second-level .gov domains, but the Directive's scope includes any domain suffix.

The actions the Directive requires increase the security of emails in transit and makes it easier to detect emails that attempt to spoof .gov domains. This protects intra-government users and the general public equally. See https://cyber.dhs.gov/bod/18-01/#introduction-to-email-authentication for more information about email authentication, as well as https://cyber.dhs.gov/bod/18-01/#compliance-guide and https://cyber.dhs.gov/bod/18-01/#frequently-asked-questions for a compliance guide and FAQ, respectively.

If you believe our reporting or methodology is in error, let us know. If the flaw appears tool-related, we encourage you to file an issue on our open-source scanner at https://github.com/cisagov/trustymail.

We welcome your feedback and questions.

Cheers,
The NCATS Team

National Cybersecurity Assessments and Technical Services (NCATS)
Cybersecurity and Infrastructure Security Agency (CISA)
vulnerability@cisa.dhs.gov

----changelog----
12/11/2017
* Known issue: The fed.us TLD is inaccurately represented in some reports.
03/29/2019
* If an SMTP-responsive hostname does not have an SPF record set, but it is covered by a valid DMARC record with a policy of reject, we now count the hostname as compliant with respect to SPF.  This change is being made to more closely align with the exact language in BOD 18-01.  As a result, users may see an increase in SPF record compliance scores.
-----------------
"""
                self.assertEqual(part.get_payload(), body)
            elif part.get_content_type() == "text/html":
                html_body = """<html>
<head></head>
<body>
<div style=""font-size:14.5"">
<p>Greetings CLARKE,</p>
<p>Attached is your <b>Trustworthy Email Report</b>. This report presents your organization's support of SPF and DMARC, two email authentication standards, as published at your .gov domains. The data in this report comes from a <b>scan that took place on December 15, 2001.</b></p>
<p><a href="https://cyber.dhs.gov/bod/18-01/">CISA Binding Operational Directive 18-01</a> requires your agency to take certain actions relevant to the data in this report:</p>
<ul>
<li>Within 90 days of BOD issuance, configure all second-level domains to have valid SPF/DMARC records, with at minimum a DMARC policy of &ldquo;p=none&rdquo; and at least one address defined as a recipient of aggregate and/or failure reports.</li>
<li>Within one year of BOD issuance, set a DMARC policy of &ldquo;reject&rdquo; for all second-level domains and mail-sending hosts.</li>
<li>(The Directive additionally requires all internet-facing mail servers to offer STARTTLS. This data will be represented in the Trustworthy Email Report in December.</li>
</ul>
</p>
<p>Raw results in this Report are available as a CSV in the Appendix, which includes error messages. Note that this report includes data from second-level .gov domains, but the Directive's <a href="https://cyber.dhs.gov/bod/18-01/#what-is-the-scope-of-bod-18-01">scope includes any domain suffix</a>.</p>
<p>The actions the Directive requires increases the security of emails in transit and makes it easier to detect emails that attempt to spoof .gov domains. This protects intra-government users and the general public equally. See <a href="https://cyber.dhs.gov/bod/18-01/#introduction-to-email-authentication">cyber.dhs.gov/bod/18-01/#introduction-to-email-authentication</a> for more information about email authentication, as well as <a href="https://cyber.dhs.gov/bod/18-01/#compliance-guide">cyber.dhs.gov/bod/18-01/#compliance-guide</a> and <a href="https://cyber.dhs.gov/bod/18-01/#frequently-asked-questions">cyber.dhs.gov/bod/18-01/#frequently-asked-questions</a> for a compliance guide and FAQ, respectively.</p>
<p>If you believe our reporting or methodology is in error, let us know. If the flaw appears tool-related, we encourage you to <a href="https://github.com/cisagov/trustymail">file an issue</a> on our open-source scanner.</p>
<p>We welcome your feedback and questions.</p>
Cheers,<br>
The NCATS Team<br><br />
National Cybersecurity Assessments and Technical Services (NCATS)<br />
Cybersecurity and Infrastructure Security Agency (CISA)<br />
<a href=""mailto:vulnerability@cisa.dhs.gov"">vulnerability@cisa.dhs.gov</a></p>
</div></p><br>
<p>----changelog----</p>
<p><i>12/11/2017</i></p>
<b>* Known issue:</b> The fed.us TLD is inaccurately represented in some reports.</p>
<p><i>03/29/2019</i></p>
<b>* </b> If an SMTP-responsive hostname does not have an SPF record set, but it is covered by a valid DMARC record with a policy of reject, we now count the hostname as compliant with respect to SPF.  This change is being made to more closely align with the exact language in BOD 18-01.  As a result, users may see an increase in SPF record compliance scores. </p>
<p>--------------------</p>
</body>
</html>
"""
                self.assertEqual(part.get_payload(), html_body)

    def test_six_params_single_cc(self):
        """Test the 6-parameter version of the constructor."""
        to = ["recipient@example.com", "recipient2@example.com"]
        pdf = "./tests/data/pdf-sample.pdf"
        fm = "sender@example.com"
        cc = ["cc@example.com"]
        bcc = ["bcc@example.com"]
        agency_acronym = "CLARKE"
        report_date = "December 15, 2001"

        message = TmailMessage(
            to,
            pdf,
            agency_acronym,
            report_date,
            from_addr=fm,
            cc_addrs=cc,
            bcc_addrs=bcc,
        )

        self.assertEqual(message["From"], fm)
        self.assertEqual(
            message["Subject"],
            "CLARKE - Trustworthy Email Report - December 15, 2001 Results",
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

Attached is your Trustworthy Email Report. This report presents your organization's support of SPF and DMARC, two email authentication standards, as published at your .gov domains. The data in this report comes from a scan that took place on December 15, 2001.

CISA Binding Operational Directive 18-01 requires your agency to take certain actions relevant to the data in this report:
* Within 90 days of BOD issuance, configure all second-level domains to have valid SPF/DMARC records, with at minimum a DMARC policy of "p=none" and at least one address defined as a recipient of aggregate and/or failure reports.
* Within one year of BOD issuance, set a DMARC policy of "reject" for all second-level domains and mail-sending hosts.
* The Directive additionally requires all internet-facing mail servers to offer STARTTLS. This data will be represented in the Trustworthy Email Report in December.

Raw results in this Report are available as a CSV in the Appendix, which includes error messages. Note that this report includes data from second-level .gov domains, but the Directive's scope includes any domain suffix.

The actions the Directive requires increase the security of emails in transit and makes it easier to detect emails that attempt to spoof .gov domains. This protects intra-government users and the general public equally. See https://cyber.dhs.gov/bod/18-01/#introduction-to-email-authentication for more information about email authentication, as well as https://cyber.dhs.gov/bod/18-01/#compliance-guide and https://cyber.dhs.gov/bod/18-01/#frequently-asked-questions for a compliance guide and FAQ, respectively.

If you believe our reporting or methodology is in error, let us know. If the flaw appears tool-related, we encourage you to file an issue on our open-source scanner at https://github.com/cisagov/trustymail.

We welcome your feedback and questions.

Cheers,
The NCATS Team

National Cybersecurity Assessments and Technical Services (NCATS)
Cybersecurity and Infrastructure Security Agency (CISA)
vulnerability@cisa.dhs.gov

----changelog----
12/11/2017
* Known issue: The fed.us TLD is inaccurately represented in some reports.
03/29/2019
* If an SMTP-responsive hostname does not have an SPF record set, but it is covered by a valid DMARC record with a policy of reject, we now count the hostname as compliant with respect to SPF.  This change is being made to more closely align with the exact language in BOD 18-01.  As a result, users may see an increase in SPF record compliance scores.
-----------------
"""
                self.assertEqual(part.get_payload(), body)
            elif part.get_content_type() == "text/html":
                html_body = """<html>
<head></head>
<body>
<div style=""font-size:14.5"">
<p>Greetings CLARKE,</p>
<p>Attached is your <b>Trustworthy Email Report</b>. This report presents your organization's support of SPF and DMARC, two email authentication standards, as published at your .gov domains. The data in this report comes from a <b>scan that took place on December 15, 2001.</b></p>
<p><a href="https://cyber.dhs.gov/bod/18-01/">CISA Binding Operational Directive 18-01</a> requires your agency to take certain actions relevant to the data in this report:</p>
<ul>
<li>Within 90 days of BOD issuance, configure all second-level domains to have valid SPF/DMARC records, with at minimum a DMARC policy of &ldquo;p=none&rdquo; and at least one address defined as a recipient of aggregate and/or failure reports.</li>
<li>Within one year of BOD issuance, set a DMARC policy of &ldquo;reject&rdquo; for all second-level domains and mail-sending hosts.</li>
<li>(The Directive additionally requires all internet-facing mail servers to offer STARTTLS. This data will be represented in the Trustworthy Email Report in December.</li>
</ul>
</p>
<p>Raw results in this Report are available as a CSV in the Appendix, which includes error messages. Note that this report includes data from second-level .gov domains, but the Directive's <a href="https://cyber.dhs.gov/bod/18-01/#what-is-the-scope-of-bod-18-01">scope includes any domain suffix</a>.</p>
<p>The actions the Directive requires increases the security of emails in transit and makes it easier to detect emails that attempt to spoof .gov domains. This protects intra-government users and the general public equally. See <a href="https://cyber.dhs.gov/bod/18-01/#introduction-to-email-authentication">cyber.dhs.gov/bod/18-01/#introduction-to-email-authentication</a> for more information about email authentication, as well as <a href="https://cyber.dhs.gov/bod/18-01/#compliance-guide">cyber.dhs.gov/bod/18-01/#compliance-guide</a> and <a href="https://cyber.dhs.gov/bod/18-01/#frequently-asked-questions">cyber.dhs.gov/bod/18-01/#frequently-asked-questions</a> for a compliance guide and FAQ, respectively.</p>
<p>If you believe our reporting or methodology is in error, let us know. If the flaw appears tool-related, we encourage you to <a href="https://github.com/cisagov/trustymail">file an issue</a> on our open-source scanner.</p>
<p>We welcome your feedback and questions.</p>
Cheers,<br>
The NCATS Team<br><br />
National Cybersecurity Assessments and Technical Services (NCATS)<br />
Cybersecurity and Infrastructure Security Agency (CISA)<br />
<a href=""mailto:vulnerability@cisa.dhs.gov"">vulnerability@cisa.dhs.gov</a></p>
</div></p><br>
<p>----changelog----</p>
<p><i>12/11/2017</i></p>
<b>* Known issue:</b> The fed.us TLD is inaccurately represented in some reports.</p>
<p><i>03/29/2019</i></p>
<b>* </b> If an SMTP-responsive hostname does not have an SPF record set, but it is covered by a valid DMARC record with a policy of reject, we now count the hostname as compliant with respect to SPF.  This change is being made to more closely align with the exact language in BOD 18-01.  As a result, users may see an increase in SPF record compliance scores. </p>
<p>--------------------</p>
</body>
</html>
"""
                self.assertEqual(part.get_payload(), html_body)

    def test_six_params_multiple_cc(self):
        """Test the 6-parameter version of the constructor."""
        to = ["recipient@example.com", "recipient2@example.com"]
        pdf = "./tests/data/pdf-sample.pdf"
        fm = "sender@example.com"
        cc = ["cc@example.com", "cc2@example.com"]
        bcc = ["bcc@example.com", "bcc2@example.com"]
        agency_acronym = "CLARKE"
        report_date = "December 15, 2001"

        message = TmailMessage(
            to,
            pdf,
            agency_acronym,
            report_date,
            from_addr=fm,
            cc_addrs=cc,
            bcc_addrs=bcc,
        )

        self.assertEqual(message["From"], fm)
        self.assertEqual(
            message["Subject"],
            "CLARKE - Trustworthy Email Report - December 15, 2001 Results",
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

Attached is your Trustworthy Email Report. This report presents your organization's support of SPF and DMARC, two email authentication standards, as published at your .gov domains. The data in this report comes from a scan that took place on December 15, 2001.

CISA Binding Operational Directive 18-01 requires your agency to take certain actions relevant to the data in this report:
* Within 90 days of BOD issuance, configure all second-level domains to have valid SPF/DMARC records, with at minimum a DMARC policy of "p=none" and at least one address defined as a recipient of aggregate and/or failure reports.
* Within one year of BOD issuance, set a DMARC policy of "reject" for all second-level domains and mail-sending hosts.
* The Directive additionally requires all internet-facing mail servers to offer STARTTLS. This data will be represented in the Trustworthy Email Report in December.

Raw results in this Report are available as a CSV in the Appendix, which includes error messages. Note that this report includes data from second-level .gov domains, but the Directive's scope includes any domain suffix.

The actions the Directive requires increase the security of emails in transit and makes it easier to detect emails that attempt to spoof .gov domains. This protects intra-government users and the general public equally. See https://cyber.dhs.gov/bod/18-01/#introduction-to-email-authentication for more information about email authentication, as well as https://cyber.dhs.gov/bod/18-01/#compliance-guide and https://cyber.dhs.gov/bod/18-01/#frequently-asked-questions for a compliance guide and FAQ, respectively.

If you believe our reporting or methodology is in error, let us know. If the flaw appears tool-related, we encourage you to file an issue on our open-source scanner at https://github.com/cisagov/trustymail.

We welcome your feedback and questions.

Cheers,
The NCATS Team

National Cybersecurity Assessments and Technical Services (NCATS)
Cybersecurity and Infrastructure Security Agency (CISA)
vulnerability@cisa.dhs.gov

----changelog----
12/11/2017
* Known issue: The fed.us TLD is inaccurately represented in some reports.
03/29/2019
* If an SMTP-responsive hostname does not have an SPF record set, but it is covered by a valid DMARC record with a policy of reject, we now count the hostname as compliant with respect to SPF.  This change is being made to more closely align with the exact language in BOD 18-01.  As a result, users may see an increase in SPF record compliance scores.
-----------------
"""
                self.assertEqual(part.get_payload(), body)
            elif part.get_content_type() == "text/html":
                html_body = """<html>
<head></head>
<body>
<div style=""font-size:14.5"">
<p>Greetings CLARKE,</p>
<p>Attached is your <b>Trustworthy Email Report</b>. This report presents your organization's support of SPF and DMARC, two email authentication standards, as published at your .gov domains. The data in this report comes from a <b>scan that took place on December 15, 2001.</b></p>
<p><a href="https://cyber.dhs.gov/bod/18-01/">CISA Binding Operational Directive 18-01</a> requires your agency to take certain actions relevant to the data in this report:</p>
<ul>
<li>Within 90 days of BOD issuance, configure all second-level domains to have valid SPF/DMARC records, with at minimum a DMARC policy of &ldquo;p=none&rdquo; and at least one address defined as a recipient of aggregate and/or failure reports.</li>
<li>Within one year of BOD issuance, set a DMARC policy of &ldquo;reject&rdquo; for all second-level domains and mail-sending hosts.</li>
<li>(The Directive additionally requires all internet-facing mail servers to offer STARTTLS. This data will be represented in the Trustworthy Email Report in December.</li>
</ul>
</p>
<p>Raw results in this Report are available as a CSV in the Appendix, which includes error messages. Note that this report includes data from second-level .gov domains, but the Directive's <a href="https://cyber.dhs.gov/bod/18-01/#what-is-the-scope-of-bod-18-01">scope includes any domain suffix</a>.</p>
<p>The actions the Directive requires increases the security of emails in transit and makes it easier to detect emails that attempt to spoof .gov domains. This protects intra-government users and the general public equally. See <a href="https://cyber.dhs.gov/bod/18-01/#introduction-to-email-authentication">cyber.dhs.gov/bod/18-01/#introduction-to-email-authentication</a> for more information about email authentication, as well as <a href="https://cyber.dhs.gov/bod/18-01/#compliance-guide">cyber.dhs.gov/bod/18-01/#compliance-guide</a> and <a href="https://cyber.dhs.gov/bod/18-01/#frequently-asked-questions">cyber.dhs.gov/bod/18-01/#frequently-asked-questions</a> for a compliance guide and FAQ, respectively.</p>
<p>If you believe our reporting or methodology is in error, let us know. If the flaw appears tool-related, we encourage you to <a href="https://github.com/cisagov/trustymail">file an issue</a> on our open-source scanner.</p>
<p>We welcome your feedback and questions.</p>
Cheers,<br>
The NCATS Team<br><br />
National Cybersecurity Assessments and Technical Services (NCATS)<br />
Cybersecurity and Infrastructure Security Agency (CISA)<br />
<a href=""mailto:vulnerability@cisa.dhs.gov"">vulnerability@cisa.dhs.gov</a></p>
</div></p><br>
<p>----changelog----</p>
<p><i>12/11/2017</i></p>
<b>* Known issue:</b> The fed.us TLD is inaccurately represented in some reports.</p>
<p><i>03/29/2019</i></p>
<b>* </b> If an SMTP-responsive hostname does not have an SPF record set, but it is covered by a valid DMARC record with a policy of reject, we now count the hostname as compliant with respect to SPF.  This change is being made to more closely align with the exact language in BOD 18-01.  As a result, users may see an increase in SPF record compliance scores. </p>
<p>--------------------</p>
</body>
</html>
"""
                self.assertEqual(part.get_payload(), html_body)


if __name__ == "__main__":
    unittest.main()
