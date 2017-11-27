import unittest

from cyhy.mailer.CyhyMessage import CyhyMessage


class Test(unittest.TestCase):

    def test_two_params_single_recipient(self):
        message = CyhyMessage(['recipient@example.com'], './tests/data/pdf-sample.pdf')
        self.assertEqual(message['From'], CyhyMessage.DefaultFrom)


if __name__ == '__main__':
    unittest.main()
