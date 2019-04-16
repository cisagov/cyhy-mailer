import pystache

from cyhy.mailer.Message import Message
from cyhy.mailer.ReportMessage import ReportMessage


class HttpsMessage(ReportMessage):
    """A class representing an email message with an HTTPS report
    PDF attachment.

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

    TextBody = """Greetings {{acronym}},

Attached is your latest HTTPS Report.

This report is intended to assist your agency in complying with OMB M-15-13 and CISA Binding Operational Directive 18-01.

This report includes all second-level .gov domains your agency owns and many known subdomains. Subdomains are gleaned from Cyber Hygiene scans, the General Services Administration's Digital Analytics Program, Censys.io, and data from the End of Term Web Archive. The data in this report comes from a scan that took place on {{report_date}}.

The embedded CSV, pshtt-results.csv, contains the raw scores for compliance. For domains where "Live" == "True", when "Domain Supports HTTPS", "Domain Enforces HTTPS", and "Domain Uses Strong HSTS" are all "True", OR where "HSTS Base Domain Preloaded" is "True", that domain is M-15-13 compliant. Domains where "Live" == "False" are not web-responsive and do not fall under M-15-13's scope.

We welcome your feedback and questions.

Cheers,
The NCATS Team

National Cybersecurity Assessments and Technical Services (NCATS)
Cybersecurity and Infrastructure Security Agency (CISA)
ncats@hq.dhs.gov

----changelog----
03/28/2017
* Fixed: Compliance scores in the "Executive Summary" now account for preloaded domains. Preloading is OMB's preferred method for HSTS compliance.

02/15/2017
* Fixed an issue where some hostnames would appear twice in pshtt-results.csv
* Fixed: A local caching error caused domains that have been HSTS preloaded after December 19th, 2016 to be reported incorrectly
* Known issue: Compliance scores in the "Executive Summary" section are not yet accounting for preloaded domains

01/25/2017
* Fixed: A flaw in the report logic would sometimes cause the "Results" section of the PDF to inaccurately represent raw pshtt scores. This error would also represent domains that were "HSTS Preload Ready" or "HSTS Preload Pending" as preloaded (a checkmark).
* Added: The report will now represent domains with "bad chain" errors (but not hostname or expired certificate errors) that otherwise satisfy M-15-13 as compliant. This is in line with M-15-13 not requiring the use of a particular certificate authority
--------------------
"""

    HtmlBody = """<html>
<head></head>
<body>
<div style=""font-size:14.5"">
<p>Greetings {{acronym}},</p>
<p>Attached is your latest HTTPS Report.</p>
<p>This report is intended to assist your agency in complying with OMB <a href="https://https.cio.gov">M-15-13</a> and CISA <a href="https://cyber.dhs.gov/bod/18-01/">Binding Operational Directive 18-01</a>.</p>
<p>This report includes all second-level .gov domains your agency owns and many known subdomains. Subdomains are gleaned from Cyber Hygiene scans, the General Services Administration's <a href="https://analytics.usa.gov/">Digital Analytics Program</a>, <a href=https://censys.io>Censys.io</a>, and data from the <a href="http://eotarchive.cdlib.org/">End of Term Web Archive</a>. The data in this report comes from a <b>scan that took place on {{report_date}}.</b></p>
<p>The embedded CSV, pshtt-results.csv, contains the raw scores for compliance. <i>For domains where &ldquo;Live&rdquo; == &ldquo;True&rdquo;</i>, when &ldquo;Domain Supports HTTPS&rdquo;, &ldquo;Domain Enforces HTTPS&rdquo;, and &ldquo;Domain Uses Strong HSTS&rdquo; are all &ldquo;True&rdquo;, OR where &ldquo;HSTS Base Domain Preloaded&rdquo; is &ldquo;True&rdquo;, that domain is M-15-13 compliant. Domains where &ldquo;Live&rdquo; == &ldquo;False&rdquo; are not web-responsive and do not fall under M-15-13's scope.</p>
<p>We welcome your feedback and questions.</p>
Cheers,<br>
The NCATS Team<br><br />
National Cybersecurity Assessments and Technical Services (NCATS)<br />
Cybersecurity and Infrastructure Security Agency (CISA)<br />
<a href=""mailto:ncats@hq.dhs.gov""> ncats@hq.dhs.gov </a>
</p>
</div>
</p><br>
<p>----changelog----</p>
<p><i>03/28/2017</i></p>
<p><b>* Fixed:</b> Compliance scores in the &ldquo;Executive Summary&rdquo; now account for preloaded domains. Preloading is OMB's <a href="https://https.cio.gov/guide/#options-for-hsts-compliance">preferred method</a> for HSTS compliance.</p></p>
<p><i>02/15/2017</i></p>
<p><b>* Fixed</b> an issue where some hostnames would appear twice in<b> pshtt-results.csv <br>
* Fixed: </b>A local caching error caused domains that have been HSTS preloaded after December 19th, 2016 to be reported incorrectly<br>
<b>* Known issue</b>: Compliance scores in the &ldquo;Executive Summary&rdquo; section are not yet accounting for preloaded domains</p>
<p><i>01/25/2017</i></p>
<p><b>* Fixed</b>: A flaw in the report logic would sometimes cause the &ldquo;Results&rdquo; section of the PDF to inaccurately represent raw pshtt scores. This error would also represent domains that were &ldquo;HSTS Preload Ready&rdquo; or &ldquo;HSTS Preload Pending&rdquo; as preloaded (a checkmark).<br>
<b>* Added</b>: The report will now represent domains with &ldquo;bad chain&rdquo; errors (but not hostname or expired certificate errors) that otherwise satisfy M-15-13 as compliant. This is in line with M-15-13 <a href="https://https.cio.gov/certificates/#are-there-federal-restrictions-on-acceptable-certificate-authorities-to-use%3f">not requiring the use of a particular certificate authority</a>.</p>
<p>--------------------</p>
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
            The filename of the PDF file that is the Trustworthy Email
            report corresponding to this message.

        agency_acronym : str
            The acronym used by the agency corresponding to the
            Trustworthy Email report attachment.

        report_date : str
            The date corresponding to the Trustworthy Email report
            attachment.  We have been using dates of the form December
            12, 2017.

        from_addr : str
            The email address from which this message is to be sent.

        cc_addrs : array of str
            An array of string objects, each of which is a CC email
            address to which this message should be sent.
        """
        # This is the data mustache will use to render the templates
        mustache_data = {"acronym": agency_acronym, "report_date": report_date}

        # Render the templates
        subject = pystache.render(HttpsMessage.Subject, mustache_data)
        text_body = pystache.render(HttpsMessage.TextBody, mustache_data)
        html_body = pystache.render(HttpsMessage.HtmlBody, mustache_data)

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
