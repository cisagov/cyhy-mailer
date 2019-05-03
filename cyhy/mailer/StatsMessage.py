"""This module contains the StatsMessage class."""

import datetime

import pystache

from cyhy.mailer.Message import Message


class StatsMessage(Message):
    """An email message containing summary statistics for a run.

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

    Subject = "cyhy-mailer summary from {{date}}"

    TextBody = """Greetings!

Here is the cyhy-mailer summary from the run ending at {{date}}:
{{#strings}}
* {{string}}
{{/strings}}

Please direct feedback and questions to ncats-dev@beta.dhs.gov and/or the cyhy-mailer GitHub project.

Regards,
The NCATS Development Team

National Cybersecurity Assessments and Technical Services (NCATS)
Cybersecurity and Infrastructure Security Agency
ncats-dev@beta.dhs.gov
"""

    HtmlBody = """<html>
<head></head>
<body>
<div style="font-size:14.5">
<p>Greetings!</p>

<p>
Here is the cyhy-mailer summary from {{date}}:
<ul>
{{#strings}}
<li>{{string}}</li>
{{/strings}}
</ul>
</p>

<p> Please direct feedback and questions to <a
href="mailto:ncats-dev@beta.dhs.gov">the NCATS Development Team</a>
and/or the <a
href="https://github.com/dhs-ncats/cyhy-mailer">cyhy-mailer GitHub
project</a>.</p>

<p>
Regards,<br>
The NCATS Development Team<br><br>
National Cybersecurity Assessments and Technical Services (NCATS)<br>
Cybersecurity and Infrastructure Security Agency<br>
<a href="mailto:ncats-dev@beta.dhs.gov">ncats-dev@beta.dhs.gov</a>
</div>
</body>
</html>
"""

    def __init__(self, to_addrs, list_of_strings):
        """Construct an instance.

        Parameters
        ----------
        to_addrs : array of str
            An array of string objects, each of which is an email
            address to which this message should be sent.

        list_of_strings : array of str
            An array of string objects, each of which is a statement
            about the cyhy-mailer run.

        """
        # Grab the current date
        now = datetime.datetime.utcnow()
        # The microseconds are irrelevant and just make everything
        # look confusing
        now = now.replace(microsecond=0)
        # This is the data mustache will use to render the templates
        mustache_data = {
            "date": now.isoformat(),
            "strings": [{"string": s} for s in list_of_strings],
        }

        # Render the templates
        subject = pystache.render(StatsMessage.Subject, mustache_data)
        text_body = pystache.render(StatsMessage.TextBody, mustache_data)
        html_body = pystache.render(StatsMessage.HtmlBody, mustache_data)

        Message.__init__(self, to_addrs, subject, text_body, html_body, cc_addrs=[])
