"""This module contains the tests for the StatsMessage class."""

# Standard Python Libraries
import datetime
import unittest

# cisagov Libraries
from cyhy.mailer.StatsMessage import StatsMessage


class Test(unittest.TestCase):
    """The tests for the StatsMessage class."""

    def test_single_string(self):
        """Test the constructor with a single string."""
        to = ["recipient@example.com"]
        strings = ["First string"]
        date = datetime.datetime.utcnow().replace(microsecond=0).isoformat()

        message = StatsMessage(to, strings)

        self.assertEqual(message["From"], "reports@cyber.dhs.gov")
        self.assertEqual(message["Subject"], "cyhy-mailer summary from {}".format(date))
        self.assertEqual(message.get("CC"), None)
        self.assertEqual(message["BCC"], "cyhy_reports@hq.dhs.gov")
        self.assertEqual(message["To"], "recipient@example.com")

        # Make sure the correct body and PDF attachments were added
        for part in message.walk():
            # multipart/* are just containers
            if part.get_content_type() == "text/plain":
                text_body = """Greetings!

Here is the cyhy-mailer summary from the run ending at {}:
* First string

Please direct feedback and questions to vm-dev@gwe.cisa.dhs.gov and/or the cyhy-mailer GitHub project.

Regards,
The VM Development Team
Cybersecurity and Infrastructure Security Agency (CISA)
vm-dev@gwe.cisa.dhs.gov
""".format(
                    date
                )
                self.assertEqual(part.get_payload(), text_body)
            elif part.get_content_type() == "text/html":
                html_body = """<html>
<head></head>
<body>
<div style="font-size:14.5">
<p>Greetings!</p>

<p>
Here is the cyhy-mailer summary from {}:
<ul>
<li>First string</li>
</ul>
</p>

<p> Please direct feedback and questions to <a
href="mailto:vm-dev@gwe.cisa.dhs.gov">the VM Development Team</a>
and/or the <a
href="https://github.com/cisagov/cyhy-mailer">cyhy-mailer GitHub
project</a>.</p>

<p>
Regards,<br>
The VM Development Team<br><br>
Cybersecurity and Infrastructure Security Agency<br>
<a href="mailto:vm-dev@gwe.cisa.dhs.gov">vm-dev@gwe.cisa.dhs.gov</a>
</div>
</body>
</html>
""".format(
                    date
                )
                self.assertEqual(part.get_payload(), html_body)

    def test_multiple_strings(self):
        """Test the constructor with multiple strings."""
        to = ["recipient@example.com"]
        strings = ["First string", "Second string"]
        date = datetime.datetime.utcnow().replace(microsecond=0).isoformat()

        message = StatsMessage(to, strings)

        self.assertEqual(message["From"], "reports@cyber.dhs.gov")
        self.assertEqual(message["Subject"], "cyhy-mailer summary from {}".format(date))
        self.assertEqual(message.get("CC"), None)
        self.assertEqual(message["BCC"], "cyhy_reports@hq.dhs.gov")
        self.assertEqual(message["To"], "recipient@example.com")

        # Make sure the correct body and PDF attachments were added
        for part in message.walk():
            # multipart/* are just containers
            if part.get_content_type() == "text/plain":
                text_body = """Greetings!

Here is the cyhy-mailer summary from the run ending at {}:
* First string
* Second string

Please direct feedback and questions to vm-dev@gwe.cisa.dhs.gov and/or the cyhy-mailer GitHub project.

Regards,
The VM Development Team
Cybersecurity and Infrastructure Security Agency (CISA)
vm-dev@gwe.cisa.dhs.gov
""".format(
                    date
                )
                self.assertEqual(part.get_payload(), text_body)
            elif part.get_content_type() == "text/html":
                html_body = """<html>
<head></head>
<body>
<div style="font-size:14.5">
<p>Greetings!</p>

<p>
Here is the cyhy-mailer summary from {}:
<ul>
<li>First string</li>
<li>Second string</li>
</ul>
</p>

<p> Please direct feedback and questions to <a
href="mailto:vm-dev@gwe.cisa.dhs.gov">the VM Development Team</a>
and/or the <a
href="https://github.com/cisagov/cyhy-mailer">cyhy-mailer GitHub
project</a>.</p>

<p>
Regards,<br>
The VM Development Team<br><br>
Cybersecurity and Infrastructure Security Agency<br>
<a href="mailto:vm-dev@gwe.cisa.dhs.gov">vm-dev@gwe.cisa.dhs.gov</a>
</div>
</body>
</html>
""".format(
                    date
                )
                self.assertEqual(part.get_payload(), html_body)


if __name__ == "__main__":
    unittest.main()
