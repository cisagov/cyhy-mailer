import unittest

from cyhy.mailer.CyhyMessage import CyhyMessage


class Test(unittest.TestCase):

    def test_two_params_single_recipient(self):
        to = ['recipient@example.com']
        pdf = './tests/data/pdf-sample.pdf'

        message = CyhyMessage(to, pdf)

        self.assertEqual(message['From'], CyhyMessage.DefaultFrom)
        self.assertEqual(message['Subject'], CyhyMessage.Subject)
        self.assertEqual(message['CC'], ','.join(CyhyMessage.DefaultCc))
        self.assertEqual(message['To'], ','.join(to))

        # Grab the bytes that comprise the attachment
        bytes = open(pdf, 'rb').read()

        # Make sure the correct attachment was added
        for part in message.walk():
            # multipart/* are just containers
            if part.get_content_type() == 'application/pdf':
                self.assertEqual(part.get_payload(decode=True), bytes)

    def test_two_params_multiple_recipients(self):
        to = ['recipient@example.com', 'recipient2@example.com']
        pdf = './tests/data/pdf-sample.pdf'

        message = CyhyMessage(to, pdf)

        self.assertEqual(message['From'], CyhyMessage.DefaultFrom)
        self.assertEqual(message['Subject'], CyhyMessage.Subject)
        self.assertEqual(message['CC'], ','.join(CyhyMessage.DefaultCc))
        self.assertEqual(message['To'], ','.join(to))

        # Grab the bytes that comprise the attachment
        bytes = open(pdf, 'rb').read()

        # Make sure the correct attachment was added
        for part in message.walk():
            # multipart/* are just containers
            if part.get_content_type() == 'application/pdf':
                self.assertEqual(part.get_payload(decode=True), bytes)

    def test_four_params_single_cc(self):
        to = ['recipient@example.com', 'recipient2@example.com']
        pdf = './tests/data/pdf-sample.pdf'
        fm = 'sender@example.com'
        cc = ['cc@example.com']

        message = CyhyMessage(to, pdf, from_addr=fm, cc_addrs=cc)

        self.assertEqual(message['From'], fm)
        self.assertEqual(message['Subject'], CyhyMessage.Subject)
        self.assertEqual(message['CC'], ','.join(cc))
        self.assertEqual(message['To'], ','.join(to))

        # Grab the bytes that comprise the attachment
        bytes = open(pdf, 'rb').read()

        # Make sure the correct attachment was added
        for part in message.walk():
            # multipart/* are just containers
            if part.get_content_type() == 'application/pdf':
                self.assertEqual(part.get_payload(decode=True), bytes)

    def test_four_params_multiple_cc(self):
        to = ['recipient@example.com', 'recipient2@example.com']
        pdf = './tests/data/pdf-sample.pdf'
        fm = 'sender@example.com'
        cc = ['cc@example.com', 'cc2@example.com']

        message = CyhyMessage(to, pdf, from_addr=fm, cc_addrs=cc)

        self.assertEqual(message['From'], fm)
        self.assertEqual(message['Subject'], CyhyMessage.Subject)
        self.assertEqual(message['CC'], ','.join(cc))
        self.assertEqual(message['To'], ','.join(to))

        # Grab the bytes that comprise the attachment
        bytes = open(pdf, 'rb').read()

        # Make sure the correct attachment was added
        for part in message.walk():
            # multipart/* are just containers
            if part.get_content_type() == 'application/pdf':
                self.assertEqual(part.get_payload(decode=True), bytes)


if __name__ == '__main__':
    unittest.main()
