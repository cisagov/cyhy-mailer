"""This module contains the HttpsMessage class."""

# Third-Party Libraries
import chevron

# cisagov Libraries
from cyhy.mailer.Message import Message
from cyhy.mailer.ReportMessage import ReportMessage


class HttpsMessage(ReportMessage):
    """An email message with an HTTPS report PDF attachment.

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

    Subject = "{{acronym}} - HTTPS Report - {{report_date}} Results"

    TextBody = """Greetings {{name}} ({{acronym}}),

Attached is your latest HTTPS Report.

This report is intended to assist your agency in complying with OMB M-15-13 and CISA Binding Operational Directive 18-01.

This report includes all second-level .gov domains your agency owns and many known subdomains. Subdomains are gleaned from Cyber Hygiene scans, the General Services Administration's Digital Analytics Program, and data from the End of Term Web Archive. The data in this report comes from a scan that took place on {{report_date}}.

The embedded CSV, pshtt-results.csv, contains the raw scores for compliance. For domains where "Live" == "True", when "Domain Supports HTTPS", "Domain Enforces HTTPS", and "Domain Uses Strong HSTS" are all "True", OR where "HSTS Base Domain Preloaded" is "True", that domain is M-15-13 compliant. Domains where "Live" == "False" are not web-responsive and do not fall under M-15-13's scope.

We welcome your feedback and questions.

Cheers,
CISA Cyber Assessments - Cyber Hygiene
Cybersecurity and Infrastructure Security Agency
vulnerability@cisa.dhs.gov
"""

    HtmlBody = """<html>
<head></head>
<body>
<div style=""font-size:14.5"">
<p>Greetings {{name}} ({{acronym}}),</p>
<p>Attached is your latest HTTPS Report.</p>
<p>This report is intended to assist your agency in complying with OMB M-15-13 and CISA <a href="https://www.cisa.gov/news-events/directives/bod-18-01-enhance-email-and-web-security">Binding Operational Directive 18-01</a>.</p>
<p>This report includes all second-level .gov domains your agency owns and many known subdomains. Subdomains are gleaned from Cyber Hygiene scans, the General Services Administration's <a href="https://analytics.usa.gov/">Digital Analytics Program</a>, and data from the <a href="http://eotarchive.cdlib.org/">End of Term Web Archive</a>. The data in this report comes from a <b>scan that took place on {{report_date}}.</b></p>
<p>The embedded CSV, pshtt-results.csv, contains the raw scores for compliance. <i>For domains where &ldquo;Live&rdquo; == &ldquo;True&rdquo;</i>, when &ldquo;Domain Supports HTTPS&rdquo;, &ldquo;Domain Enforces HTTPS&rdquo;, and &ldquo;Domain Uses Strong HSTS&rdquo; are all &ldquo;True&rdquo;, OR where &ldquo;HSTS Base Domain Preloaded&rdquo; is &ldquo;True&rdquo;, that domain is M-15-13 compliant. Domains where &ldquo;Live&rdquo; == &ldquo;False&rdquo; are not web-responsive and do not fall under M-15-13's scope.</p>
<p>We welcome your feedback and questions.</p>
<p>Cheers,<br>
CISA Cyber Assessments - Cyber Hygiene<br><br />
Cybersecurity and Infrastructure Security Agency<br />
<a href=""mailto:vulnerability@cisa.dhs.gov""> vulnerability@cisa.dhs.gov </a>
</p>
</div>
</body>
</html>
"""

    def __init__(
        self,
        to_addrs,
        pdf_filename,
        entity_acronym,
        entity_name,
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
            The filename of the PDF file that is the Trustworthy Email
            report corresponding to this message.

        entity_acronym : str
            The acronym used by the entity corresponding to the
            Trustworthy Email report attachment.

        entity_name : str
            The name of the entity corresponding to the Trustworthy Email
            report attachment.

        report_date : str
            The date corresponding to the Trustworthy Email report
            attachment.  We have been using dates of the form December
            12, 2017.

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
            "acronym": entity_acronym,
            "name": entity_name,
            "report_date": report_date,
        }

        # Render the templates
        subject = chevron.render(HttpsMessage.Subject, mustache_data)
        text_body = chevron.render(HttpsMessage.TextBody, mustache_data)
        html_body = chevron.render(HttpsMessage.HtmlBody, mustache_data)

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
