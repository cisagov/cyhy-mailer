"""This module contains the CyhyNotificationMessage class."""

import pystache

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

    Subject = "{{acronym}} - Cyber Hygiene Alert - New Critical/High Vulnerabilities Detected - {{report_date}}"

    TextBody = """Greetings {{acronym}},

Cyber Hygiene scans conducted in the past day indicate potential new critical and/or high vulnerabilities. As part of BOD 19-02, critical findings need to be remediated within 15 days and high findings remediated within 30 days. Details are attached. Same password as before.

If you have any questions, please contact our office.

Cheers,
The NCATS team

National Cybersecurity Assessments and Technical Services (NCATS)
Cybersecurity and Infrastructure Security Agency (CISA)
ncats@hq.dhs.gov

WARNING: This document is FOR OFFICIAL USE ONLY (FOUO). It contains information that may be exempt from public release under the Freedom of Information Act (5 U.S.G. 552). It is to be controlled, stored, handled, transmitted, distributed, and disposed of in accordance with CISA policy relating to FOUO information and is not to be released to the public or other personnel who do not have a valid 'need-to-know' without prior approval of an authorized CISA official.
"""

    HtmlBody = """<html>
<head></head>
<body>
<p>Greetings {{acronym}},</p>

<p>Cyber Hygiene scans conducted in the past day indicate potential new critical and/or high vulnerabilities. As part of <a href="https://cyber.dhs.gov/bod/19-02/">BOD 19-02</a>, critical findings need to be remediated within 15 days and high findings remediated within 30 days. Details are attached. Same password as before.</p>

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

    def __init__(
        self,
        to_addrs,
        pdf_filename,
        agency_acronym,
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
        mustache_data = {"acronym": agency_acronym, "report_date": report_date}

        # Render the templates
        subject = pystache.render(CyhyNotificationMessage.Subject, mustache_data)
        text_body = pystache.render(CyhyNotificationMessage.TextBody, mustache_data)
        html_body = pystache.render(CyhyNotificationMessage.HtmlBody, mustache_data)

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
