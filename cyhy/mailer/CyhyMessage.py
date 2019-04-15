import pystache

from cyhy.mailer.Message import Message
from cyhy.mailer.ReportMessage import ReportMessage


class CyhyMessage(ReportMessage):
    """A class representing an email message with a CYHY report PDF
    attachment.

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

    Subject = "{{acronym}} - Cyber Hygiene Report - {{report_date}} Results"

    TextBody = """Greetings {{acronym}},

The Cyber Hygiene scan results are attached for your review. Same password as before. (If this is your first report and you have yet to receive a password, please let us know!)

If you have any questions, please contact our office.

Cheers,
The NCATS team

National Cybersecurity Assessments and Technical Services (NCATS)
National Cybersecurity and Communications Integration Center
U.S. Department of Homeland Security
ncats@hq.dhs.gov

WARNING: This document is FOR OFFICIAL USE ONLY (FOUO). It contains information that may be exempt from public release under the Freedom of Information Act (5 U.S.G. 552). It is to be controlled, stored, handled, transmitted, distributed, and disposed of in accordance with DHS policy relating to FOUO information and is not to be released to the public or other personnel who do not have a valid 'need-to-know' without prior approval of an authorized DHS official.
"""

    HtmlBody = """<html>
<head></head>
<body>
<p>Greetings {{acronym}},</p>

<p>The Cyber Hygiene scan results are attached for your review. Same password as before. (If this is your first report and you have yet to receive a password, please let us know!)</p>

<p>If you have any questions, please contact our office.</p>

<p>Cheers,<br>
The NCATS team</p>

<p>National Cybersecurity Assessments and Technical Services (NCATS)<br>
National Cybersecurity and Communications Integration Center<br>
U.S. Department of Homeland Security<br>
<a href="mailto:ncats@hq.dhs.gov">ncats@hq.dhs.gov</a></p>

<p>WARNING: This document is FOR OFFICIAL USE ONLY (FOUO). It contains information that may be exempt from public release under the Freedom of Information Act (5 U.S.G. 552). It is to be controlled, stored, handled, transmitted, distributed, and disposed of in accordance with DHS policy relating to FOUO information and is not to be released to the public or other personnel who do not have a valid 'need-to-know' without prior approval of an authorized DHS official.</p>
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
    ):
        """Construct an instance.

        Parameters
        ----------
        to_addrs : array of str
            An array of string objects, each of which is an email
            address to which this message should be sent.

        pdf_filename : str
            The filename of the PDF file that is the CYHY report
            corresponding to this message.

        agency_acronym : str
            The acronym used by the agency corresponding to the CYHY
            report attachment.

        report_date : str
            The date corresponding to the CYHY report attachment.  We
            have been using dates of the form December 12, 2017.

        from_addr : str
            The email address from which this message is to be sent.

        cc_addrs : array of str
            An array of string objects, each of which is a CC email
            address to which this message should be sent.
        """
        # This is the data mustache will use to render the templates
        mustache_data = {"acronym": agency_acronym, "report_date": report_date}

        # Render the templates
        subject = pystache.render(CyhyMessage.Subject, mustache_data)
        text_body = pystache.render(CyhyMessage.TextBody, mustache_data)
        html_body = pystache.render(CyhyMessage.HtmlBody, mustache_data)

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
