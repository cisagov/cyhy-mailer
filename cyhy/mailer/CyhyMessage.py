"""This module contains the CyhyMessage class."""

import pystache

from cyhy.mailer.Message import Message
from cyhy.mailer.ReportMessage import ReportMessage


class CyhyMessage(ReportMessage):
    """An email message with a CYHY report PDF attachment.

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

The Cyber Hygiene scan results are attached for your review. Same password as before. (If this is your first report and you have yet to receive a password, please let us know.)

{{#has_tech_pocs}}
Note: NCATS has the following information listed as the Technical Points of Contact for {{acronym}}:

{{#tech_pocs}}
Name:  {{name}}
Email:  {{email}}

{{/tech_pocs}}
Please request the report password from a Technical Point of Contact and route all other requests through a Technical POC. Should a Technical Point of Contact listed above no longer be with {{acronym}}, please contact NCATS@hq.dhs.gov with updated information.

{{/has_tech_pocs}}
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

<p>The Cyber Hygiene scan results are attached for your review. Same password as before. (If this is your first report and you have yet to receive a password, please let us know.)</p>

{{#has_tech_pocs}}
<p>Note: NCATS has the following information listed as the Technical Points of Contact for {{acronym}}:</p>

{{#tech_pocs}}
<p>
Name:  {{name}}<br>
Email:  {{email}}<br>
</p>
{{/tech_pocs}}

<p>Please request the report password from a Technical Point of Contact and route all other requests through a Technical POC. Should a Technical Point of Contact listed above no longer be with {{acronym}}, please contact <a href="mailto:NCATS@hq.dhs.gov">NCATS@hq.dhs.gov</a> with updated information.</p>

{{/has_tech_pocs}}
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
        tech_pocs,
        from_addr=Message.DefaultFrom,
        cc_addrs=Message.DefaultCc,
        bcc_addrs=None,
    ):
        """Construct an instance.

        Parameters
        ----------
        to_addrs : list of str
            A list of string objects, each of which is an email
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

        tech_pocs : list of dict
            A list of dicts, each containing a "name" and an "email"
            key.  The corresponding values correspond to the name and
            email of a technical POC for the agency corresponding to
            the CYHY report attachment.  If there are no technical
            POCs for the agency then this parameter should be an empty
            list.

        from_addr : str
            The email address from which this message is to be sent.

        cc_addrs : list of str
            A list of string objects, each of which is a CC email
            address to which this message should be sent.

        bcc_addrs : list of str
            A list of string objects, each of which is a BCC email
            address to which this message should be sent.

        """
        # This is the data mustache will use to render the templates
        mustache_data = {
            "acronym": agency_acronym,
            "report_date": report_date,
            "has_tech_pocs": len(tech_pocs) != 0,
            "tech_pocs": tech_pocs,
        }

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
            bcc_addrs,
        )
