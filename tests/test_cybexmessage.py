import unittest

from cyhy.mailer.CybexMessage import CybexMessage


class Test(unittest.TestCase):

    def test_three_params(self):
        pdf = './tests/data/pdf-sample.pdf'
        csv = './tests/data/csv-sample.csv'
        report_date = 'December 15, 2001'

        message = CybexMessage(pdf, csv, csv, csv, csv, report_date)

        self.assertEqual(message['From'], 'reports@cyber.dhs.gov')
        self.assertEqual(message['Subject'], 'Cybex Report - December 15, 2001 Results')
        self.assertEqual(message['CC'], None)
        self.assertEqual(message['To'], 'ncats@hq.dhs.gov')

        # Grab the bytes that comprise the attachments
        pdf_bytes = open(pdf, 'rb').read()
        csv_text = open(csv, 'r').read()

        # Make sure the correct body, PDF, and CSV attachments were added
        for part in message.walk():
            # multipart/* are just containers
            if part.get_content_type() == 'application/pdf':
                self.assertEqual(part.get_payload(decode=True), pdf_bytes)
                self.assertEqual(part.get_filename(), 'pdf-sample.pdf')
            elif part.get_content_type() == 'text/plain':
                text_body = '''Greetings,

The Cybex report from December 15, 2001 is attached for your review.

If you have any questions, please contact our office.

Cheers,
The NCATS team

National Cybersecurity Assessments and Technical Services (NCATS)
National Cybersecurity and Communications Integration Center
U.S. Department of Homeland Security
ncats@hq.dhs.gov

WARNING: This document is FOR OFFICIAL USE ONLY (FOUO). It contains information that may be exempt from public release under the Freedom of Information Act (5 U.S.G. 552). It is to be controlled, stored, handled, transmitted, distributed, and disposed of in accordance with DHS policy relating to FOUO information and is not to be released to the public or other personnel who do not have a valid 'need-to-know' without prior approval of an authorized DHS official.
'''
                self.assertEqual(part.get_payload(), text_body)
            elif part.get_content_type() == 'text/html':
                html_body = '''<html>
<head></head>
<body>
<p>Greetings,</p>

<p>The Cybex report from December 15, 2001 is attached for your review.</p>

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
'''
                self.assertEqual(part.get_payload(), html_body)
            elif part.get_content_type() == 'text/csv':
                self.assertEqual(part.get_payload(), csv_text)
                self.assertEqual(part.get_filename(), 'csv-sample.csv')

    def test_six_params(self):
        to = ['recipient@example.com', 'recipient2@example.com']
        pdf = './tests/data/pdf-sample.pdf'
        csv = './tests/data/csv-sample.csv'
        fm = 'sender@example.com'
        cc = ['cc@example.com', 'cc2@example.com']
        report_date = 'December 15, 2001'

        message = CybexMessage(pdf, csv, csv, csv, csv, report_date, to_addrs=to, from_addr=fm, cc_addrs=cc)

        self.assertEqual(message['From'], fm)
        self.assertEqual(message['Subject'], 'Cybex Report - December 15, 2001 Results')
        self.assertEqual(message['CC'], 'cc@example.com,cc2@example.com')
        self.assertEqual(message['To'], 'recipient@example.com,recipient2@example.com')

        # Grab the bytes that comprise the attachments
        pdf_bytes = open(pdf, 'rb').read()
        csv_text = open(csv, 'r').read()

        # Make sure the correct body, PDF, and CSV attachments were added
        for part in message.walk():
            # multipart/* are just containers
            if part.get_content_type() == 'application/pdf':
                self.assertEqual(part.get_payload(decode=True), pdf_bytes)
                self.assertEqual(part.get_filename(), 'pdf-sample.pdf')
            elif part.get_content_type() == 'text/plain':
                text_body = '''Greetings,

The Cybex report from December 15, 2001 is attached for your review.

If you have any questions, please contact our office.

Cheers,
The NCATS team

National Cybersecurity Assessments and Technical Services (NCATS)
National Cybersecurity and Communications Integration Center
U.S. Department of Homeland Security
ncats@hq.dhs.gov

WARNING: This document is FOR OFFICIAL USE ONLY (FOUO). It contains information that may be exempt from public release under the Freedom of Information Act (5 U.S.G. 552). It is to be controlled, stored, handled, transmitted, distributed, and disposed of in accordance with DHS policy relating to FOUO information and is not to be released to the public or other personnel who do not have a valid 'need-to-know' without prior approval of an authorized DHS official.
'''
                self.assertEqual(part.get_payload(), text_body)
            elif part.get_content_type() == 'text/html':
                html_body = '''<html>
<head></head>
<body>
<p>Greetings,</p>

<p>The Cybex report from December 15, 2001 is attached for your review.</p>

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
'''
                self.assertEqual(part.get_payload(), html_body)
            elif part.get_content_type() == 'text/csv':
                self.assertEqual(part.get_payload(), csv_text)
                self.assertEqual(part.get_filename(), 'csv-sample.csv')


if __name__ == '__main__':
    unittest.main()
