"""This module contains the CybexMessage class."""

import pystache

from cyhy.mailer.Message import Message
from cyhy.mailer.ReportMessage import ReportMessage


class CybexMessage(ReportMessage):
    """An email message with the Cyber Exposure scorecard attachments.

    Static attributes
    -----------------
    DefaultTo : str
        The default value for the address to which the message should
        be sent.

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

    DefaultTo = ["ncats@hq.dhs.gov"]

    Subject = "Cyber Exposure Scorecard - {{report_date}} Results"

    TextBody = """Greetings,

The Cyber Exposure scorecard from {{report_date}} is attached for your review.

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
<p>Greetings,</p>

<p>The Cyber Exposure scorecard from {{report_date}} is attached for your
review.</p>

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
        pdf_filename,
        critical_open_csv_filename,
        critical_closed_csv_filename,
        high_open_csv_filename,
        high_closed_csv_filename,
        report_date,
        to_addrs=DefaultTo,
        from_addr=Message.DefaultFrom,
        cc_addrs=None,
    ):
        """Construct an instance.

        Parameters
        ----------
        pdf_filename : str
            The filename of the PDF file that is the Cybex report
            corresponding to this message.

        critical_open_csv_filename : str
            The filename of the CSV file that contains the Cybex
            report data for open critical vulnerabilities.

        critical_closed_csv_filename : str
            The filename of the CSV file that contains the Cybex
            report data for closed critical vulnerabilities.

        high_open_csv_filename : str
            The filename of the CSV file that contains the Cybex
            report data for open high vulnerabilities.

        high_closed_csv_filename : str
            The filename of the CSV file that contains the Cybex
            report data for closed high vulnerabilities.

        report_date : str
            The date corresponding to the Cybex report attachment.  We
            have been using dates of the form December 12, 2017.

        to_addrs : array of str
            An array of string objects, each of which is an email
            address to which this message should be sent.

        from_addr : str
            The email address from which this message is to be sent.

        cc_addrs : array of str
            An array of string objects, each of which is a CC email
            address to which this message should be sent.

        """
        # This is the data mustache will use to render the templates
        mustache_data = {"report_date": report_date}

        # Render the templates
        subject = pystache.render(CybexMessage.Subject, mustache_data)
        text_body = pystache.render(CybexMessage.TextBody, mustache_data)
        html_body = pystache.render(CybexMessage.HtmlBody, mustache_data)

        ReportMessage.__init__(
            self,
            to_addrs,
            subject,
            text_body,
            html_body,
            pdf_filename,
            from_addr,
            cc_addrs,
        )

        self.attach_csv(critical_open_csv_filename)
        self.attach_csv(critical_closed_csv_filename)
        self.attach_csv(high_open_csv_filename)
        self.attach_csv(high_closed_csv_filename)
