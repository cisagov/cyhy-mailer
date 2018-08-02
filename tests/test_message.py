import unittest

from cyhy.mailer.Message import Message


class Test(unittest.TestCase):

    def test_one_param_single_recipient(self):
        to = ['recipient@example.com']

        message = Message(to)

        self.assertEqual(message['From'], 'reports@cyber.dhs.gov')
        self.assertEqual(message['CC'], 'reports@cyber.dhs.gov')
        self.assertEqual(message['To'], 'recipient@example.com')

    def test_one_param_multiple_recipients(self):
        to = ['recipient@example.com', 'recipient2@example.com']

        message = Message(to)

        self.assertEqual(message['From'], 'reports@cyber.dhs.gov')
        self.assertEqual(message['CC'], 'reports@cyber.dhs.gov')
        self.assertEqual(message['To'], 'recipient@example.com,recipient2@example.com')

    def test_six_params_single_cc(self):
        to = ['recipient@example.com', 'recipient2@example.com']
        fm = 'sender@example.com'
        cc = ['cc@example.com']
        subject = 'The subject'
        text_body = 'The plain-text body'
        html_body = '<p>The HTML body</p>'

        message = Message(to, subject, text_body, html_body, from_addr=fm, cc_addrs=cc)

        self.assertEqual(message['From'], fm)
        self.assertEqual(message['Subject'], subject)
        self.assertEqual(message['CC'], 'cc@example.com')
        self.assertEqual(message['To'], 'recipient@example.com,recipient2@example.com')

        # Make sure the correct body attachments were added
        for part in message.walk():
            # multipart/* are just containers
            if part.get_content_type() == 'text/plain':
                self.assertEqual(part.get_payload(), text_body)
            elif part.get_content_type() == 'text/html':
                self.assertEqual(part.get_payload(), html_body)

    def test_six_params_multiple_cc(self):
        to = ['recipient@example.com', 'recipient2@example.com']
        fm = 'sender@example.com'
        cc = ['cc@example.com', 'cc2@example.com']
        subject = 'The subject'
        text_body = 'The plain-text body'
        html_body = '<p>The HTML body</p>'

        message = Message(to, subject, text_body, html_body, from_addr=fm, cc_addrs=cc)

        self.assertEqual(message['From'], fm)
        self.assertEqual(message['Subject'], subject)
        self.assertEqual(message['CC'], 'cc@example.com,cc2@example.com')
        self.assertEqual(message['To'], 'recipient@example.com,recipient2@example.com')

        # Make sure the correct body attachments were added
        for part in message.walk():
            # multipart/* are just containers
            if part.get_content_type() == 'text/plain':
                self.assertEqual(part.get_payload(), text_body)
            elif part.get_content_type() == 'text/html':
                self.assertEqual(part.get_payload(), html_body)


if __name__ == '__main__':
    unittest.main()
