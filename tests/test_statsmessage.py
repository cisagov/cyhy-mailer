import datetime
import unittest

from cyhy.mailer.StatsMessage import StatsMessage


class Test(unittest.TestCase):

    def test_single_string(self):
        to = ['recipient@example.com']
        strings = ['First string']
        date = datetime.datetime.utcnow().replace(microsecond=0).isoformat()

        message = StatsMessage(to, strings)

        self.assertEqual(message['From'], 'reports@cyber.dhs.gov')
        self.assertEqual(message['Subject'], 'cyhy-mailer summary from {}'.format(date))
        self.assertEqual(message['To'], 'recipient@example.com')

        # Make sure the correct body and PDF attachments were added
        for part in message.walk():
            # multipart/* are just containers
            if part.get_content_type() == 'text/plain':
                text_body = '''Bonjour!

Here is the cyhy-mailer summary from the run ending at {}:
* First string

Please direct feedback and questions to ncats-dev@beta.dhs.gov and/or the cyhy-mailer GitHub project.

Au revoir,
The NCATS Development Team

National Cybersecurity Assessments and Technical Services (NCATS)
National Cybersecurity and Communications Integration Center
U.S. Department of Homeland Security
ncats-dev@beta.dhs.gov
'''.format(date)
                self.assertEqual(part.get_payload(), text_body)
            elif part.get_content_type() == 'text/html':
                html_body = '''<html>
<head></head>
<body>
<div style="font-size:14.5">
<p>Bonjour!</p>

<p>
Here is the cyhy-mailer summary from {}:
<ul>
<li>First string</li>
</ul>
</p>

<p> Please direct feedback and questions to <a
href="mailto:ncats-dev@beta.dhs.gov">the NCATS Development Team</a>
and/or the <a
href="https://github.com/dhs-ncats/cyhy-mailer">cyhy-mailer GitHub
project</a>.</p>

<p>
Au revoir,<br>
The NCATS Development Team<br><br>
National Cybersecurity Assessments and Technical Services (NCATS)<br>
National Cybersecurity and Communications Integration Center<br>
U.S. Department of Homeland Security<br>
<a href="mailto:ncats-dev@beta.dhs.gov">ncats-dev@beta.dhs.gov</a>
</div>
</body>
</html>
'''.format(date)
                self.assertEqual(part.get_payload(), html_body)

    def test_multiple_strings(self):
        to = ['recipient@example.com']
        strings = ['First string', 'Second string']
        date = datetime.datetime.utcnow().replace(microsecond=0).isoformat()

        message = StatsMessage(to, strings)

        self.assertEqual(message['From'], 'reports@cyber.dhs.gov')
        self.assertEqual(message['Subject'], 'cyhy-mailer summary from {}'.format(date))
        self.assertEqual(message['To'], 'recipient@example.com')

        # Make sure the correct body and PDF attachments were added
        for part in message.walk():
            # multipart/* are just containers
            if part.get_content_type() == 'text/plain':
                text_body = '''Bonjour!

Here is the cyhy-mailer summary from the run ending at {}:
* First string
* Second string

Please direct feedback and questions to ncats-dev@beta.dhs.gov and/or the cyhy-mailer GitHub project.

Au revoir,
The NCATS Development Team

National Cybersecurity Assessments and Technical Services (NCATS)
National Cybersecurity and Communications Integration Center
U.S. Department of Homeland Security
ncats-dev@beta.dhs.gov
'''.format(date)
                self.assertEqual(part.get_payload(), text_body)
            elif part.get_content_type() == 'text/html':
                html_body = '''<html>
<head></head>
<body>
<div style="font-size:14.5">
<p>Bonjour!</p>

<p>
Here is the cyhy-mailer summary from {}:
<ul>
<li>First string</li>
<li>Second string</li>
</ul>
</p>

<p> Please direct feedback and questions to <a
href="mailto:ncats-dev@beta.dhs.gov">the NCATS Development Team</a>
and/or the <a
href="https://github.com/dhs-ncats/cyhy-mailer">cyhy-mailer GitHub
project</a>.</p>

<p>
Au revoir,<br>
The NCATS Development Team<br><br>
National Cybersecurity Assessments and Technical Services (NCATS)<br>
National Cybersecurity and Communications Integration Center<br>
U.S. Department of Homeland Security<br>
<a href="mailto:ncats-dev@beta.dhs.gov">ncats-dev@beta.dhs.gov</a>
</div>
</body>
</html>
'''.format(date)
                self.assertEqual(part.get_payload(), html_body)


if __name__ == '__main__':
    unittest.main()
