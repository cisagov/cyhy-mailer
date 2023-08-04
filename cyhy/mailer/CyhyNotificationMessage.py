"""This module contains the CyhyNotificationMessage class."""

# Third-Party Libraries
import chevron

# cisagov Libraries
from cyhy.mailer.Message import Message
from cyhy.mailer.ReportMessage import ReportMessage


class CyhyNotificationMessage(ReportMessage):
    """An email message with a CYHY notification PDF attachment.

    Static attributes
    -----------------
    Subject : str
        The mustache template to use when constructing the message
        subject.

    TextBody : str
        The mustache template to use when constructing the plain text
        message body.

    HtmlBody : str
        The mustache template to use when constructing the HTML
        message body.

    """

    Subject = "{{acronym}} - Cyber Hygiene Alert - {{report_date}}"

    TextBody = """Greetings {{acronym}},

Cyber Hygiene scans of your host(s) conducted in the past day have detected one or both of the following:
* New critical, high, and/or known exploited vulnerabilities
* New potentially risky services

{{#is_federal}}As part of BOD 19-02, critical findings need to be remediated within 15 days and high findings remediated within 30 days.{{/is_federal}}{{^is_federal}}CISA recommends remediating critical findings within 15 days and high findings within 30 days.{{/is_federal}}

{{#is_federal}}As part of BOD 22-01, any “known exploited” findings, regardless of severity, need to be remediated within two weeks.{{/is_federal}}{{^is_federal}}CISA recommends remediating known exploited vulnerabilities, regardless of severity, within two weeks.{{/is_federal}}

CISA also recommends reviewing hosts with potentially risky open services (e.g. RDP, Telnet, etc.), especially if they are functioning as networked management interfaces, to ensure that each service is intended to be available to the public and, where applicable, the service is up-to-date on the latest version, correctly configured, and uses strong authentication.

{{#is_federal}}As part of BOD 23-02, networked management interfaces exposed to the public internet must either be shut off or protected by capabilities that enforce access control to the interface through a policy enforcement point separate from the interface itself as part of a Zero Trust Architecture within 14 days.{{/is_federal}}

The details are in the attached PDF, which has the same password as your weekly Cyber Hygiene Vulnerability Scanning report.

If you have any questions, please contact our office.

Cheers,
CISA Cyber Assessments - Cyber Hygiene
Cybersecurity and Infrastructure Security Agency
vulnerability@cisa.dhs.gov

WARNING: This message and any attached document(s) is FOR OFFICIAL USE ONLY (FOUO). It contains information that may be exempt from public release under the Freedom of Information Act (5 U.S.G. 552). It is to be controlled, stored, handled, transmitted, distributed, and disposed of in accordance with DHS policy relating to FOUO information and is not to be released to the public or other personnel who do not have a valid "need-to-know" without prior approval of an authorized DHS official.
"""

    HtmlBody = """<html>
<head></head>
<body>
<p>Greetings {{acronym}},</p>

<p>Cyber Hygiene scans of your host(s) conducted in the past day have detected one or both of the following:
<ul>
  <li>New critical, high, and/or known exploited vulnerabilities</li>
  <li>New potentially risky services</li>
</ul>
</p>

<p>{{#is_federal}}As part of <a href="https://www.cisa.gov/news-events/directives/bod-19-02-vulnerability-remediation-requirements-internet-accessible-systems">BOD 19-02</a>, critical findings need to be remediated within 15 days and high findings remediated within 30 days.{{/is_federal}}{{^is_federal}}CISA recommends remediating critical findings within 15 days and high findings within 30 days.{{/is_federal}}</p>

<p>{{#is_federal}}As part of <a href="https://www.cisa.gov/news-events/directives/bod-22-01-reducing-significant-risk-known-exploited-vulnerabilities">BOD 22-01</a>, any “known exploited” findings, regardless of severity, need to be remediated within two weeks.{{/is_federal}}{{^is_federal}}CISA recommends remediating known exploited vulnerabilities, regardless of severity, within two weeks.{{/is_federal}}</p>

<p>CISA also recommends reviewing hosts with potentially risky open services (e.g. RDP, Telnet, etc.), <em>especially if they are functioning as networked management interfaces</em>, to ensure that each service is intended to be available to the public and, where applicable, the service is up-to-date on the latest version, correctly configured, and uses strong authentication.</p>

<p>{{#is_federal}}As part of <a href="https://www.cisa.gov/news-events/directives/binding-operational-directive-23-02">BOD 23-02</a>, networked management interfaces exposed to the public internet must either be shut off or protected by capabilities that enforce access control to the interface through a policy enforcement point separate from the interface itself as part of a Zero Trust Architecture within 14 days.{{/is_federal}}</p>

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

    def __init__(
        self,
        to_addrs,
        pdf_filename,
        agency_acronym,
        is_federal,
        report_date,
        from_addr=Message.DefaultFrom,
        cc_addrs=Message.DefaultCc,
        bcc_addrs=Message.DefaultBcc,
    ):
        """Construct an instance.

        Parameters
        ----------
        to_addrs : array of str
            An array of string objects, each of which is an email
            address to which this message should be sent.

        pdf_filename : str
            The filename of the PDF file that is the CYHY notification
            corresponding to this message.

        agency_acronym : str
            The acronym used by the agency corresponding to the CYHY
            notification attachment.

        is_federal : bool
            True if the agency is Federal, otherwise False.

        report_date : str
            The date corresponding to the CYHY notification attachment.  We
            have been using dates of the form December 12, 2017.

        from_addr : str
            The email address from which this message is to be sent.

        cc_addrs : array of str
            An array of string objects, each of which is a CC email
            address to which this message should be sent.

        bcc_addrs : array of str
            An array of string objects, each of which is a BCC email
            address to which this message should be sent.

        """
        # This is the data mustache will use to render the templates
        mustache_data = {
            "acronym": agency_acronym,
            "is_federal": is_federal,
            "report_date": report_date,
        }

        # Render the templates
        subject = chevron.render(CyhyNotificationMessage.Subject, mustache_data)
        text_body = chevron.render(CyhyNotificationMessage.TextBody, mustache_data)
        html_body = chevron.render(CyhyNotificationMessage.HtmlBody, mustache_data)

        ReportMessage.__init__(
            self,
            to_addrs,
            subject,
            text_body,
            html_body,
            pdf_filename,
            from_addr,
            cc_addrs,
            bcc_addrs,
        )
