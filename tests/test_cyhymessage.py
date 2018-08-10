import unittest

from cyhy.mailer.CyhyMessage import CyhyMessage


class Test(unittest.TestCase):

    def test_four_params_single_recipient(self):
        to = ['recipient@example.com']
        pdf = './tests/data/pdf-sample.pdf'
        agency_acronym = 'CLARKE'
        report_date = 'December 15, 2001'

        message = CyhyMessage(to, pdf, agency_acronym, report_date)

        self.assertEqual(message['From'], 'reports@ncats.cyber.dhs.gov')
        self.assertEqual(message['Subject'], 'CLARKE - Cyber Hygiene Report - December 15, 2001 Results')
        self.assertEqual(message['CC'], 'ncats@hq.dhs.gov')
        self.assertEqual(message['To'], 'recipient@example.com')

        # Grab the bytes that comprise the attachment
        bytes = open(pdf, 'rb').read()

        # Make sure the correct body and PDF attachments were added
        for part in message.walk():
            # multipart/* are just containers
            if part.get_content_type() == 'application/pdf':
                self.assertEqual(part.get_payload(decode=True), bytes)
                self.assertEqual(part.get_filename(), 'pdf-sample.pdf')
            elif part.get_content_type() == 'text/plain':
                text_body = '''Greetings CLARKE,

The Cyber Hygiene scan results are attached for your review. Same password as before. (If this is your first report and you have yet to receive a password, please let us know!)

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
<p>Greetings CLARKE,</p>

<p>The Cyber Hygiene scan results are attached for your review. Same password as before. (If this is your first report and you have yet to receive a password, please let us know!)</p>

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

    def test_four_params_multiple_recipients(self):
        to = ['recipient@example.com', 'recipient2@example.com']
        pdf = './tests/data/pdf-sample.pdf'
        agency_acronym = 'CLARKE'
        report_date = 'December 15, 2001'

        message = CyhyMessage(to, pdf, agency_acronym, report_date)

        self.assertEqual(message['From'], 'reports@ncats.cyber.dhs.gov')
        self.assertEqual(message['Subject'], 'CLARKE - Cyber Hygiene Report - December 15, 2001 Results')
        self.assertEqual(message['CC'], 'ncats@hq.dhs.gov')
        self.assertEqual(message['To'], 'recipient@example.com,recipient2@example.com')

        # Grab the bytes that comprise the attachment
        bytes = open(pdf, 'rb').read()

        # Make sure the correct body and PDF attachments were added
        for part in message.walk():
            # multipart/* are just containers
            if part.get_content_type() == 'application/pdf':
                self.assertEqual(part.get_payload(decode=True), bytes)
                self.assertEqual(part.get_filename(), 'pdf-sample.pdf')
            elif part.get_content_type() == 'text/plain':
                body = '''Greetings CLARKE,

The Cyber Hygiene scan results are attached for your review. Same password as before. (If this is your first report and you have yet to receive a password, please let us know!)

If you have any questions, please contact our office.

Cheers,
The NCATS team

National Cybersecurity Assessments and Technical Services (NCATS)
National Cybersecurity and Communications Integration Center
U.S. Department of Homeland Security
ncats@hq.dhs.gov

WARNING: This document is FOR OFFICIAL USE ONLY (FOUO). It contains information that may be exempt from public release under the Freedom of Information Act (5 U.S.G. 552). It is to be controlled, stored, handled, transmitted, distributed, and disposed of in accordance with DHS policy relating to FOUO information and is not to be released to the public or other personnel who do not have a valid 'need-to-know' without prior approval of an authorized DHS official.
'''
                self.assertEqual(part.get_payload(), body)
            elif part.get_content_type() == 'text/html':
                html_body = '''<html>
<head></head>
<body>
<p>Greetings CLARKE,</p>

<p>The Cyber Hygiene scan results are attached for your review. Same password as before. (If this is your first report and you have yet to receive a password, please let us know!)</p>

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

    def test_six_params_single_cc(self):
        to = ['recipient@example.com', 'recipient2@example.com']
        pdf = './tests/data/pdf-sample.pdf'
        fm = 'sender@example.com'
        cc = ['cc@example.com']
        agency_acronym = 'CLARKE'
        report_date = 'December 15, 2001'

        message = CyhyMessage(to, pdf, agency_acronym, report_date, from_addr=fm, cc_addrs=cc)

        self.assertEqual(message['From'], fm)
        self.assertEqual(message['Subject'], 'CLARKE - Cyber Hygiene Report - December 15, 2001 Results')
        self.assertEqual(message['CC'], 'cc@example.com')
        self.assertEqual(message['To'], 'recipient@example.com,recipient2@example.com')

        # Grab the bytes that comprise the attachment
        bytes = open(pdf, 'rb').read()

        # Make sure the correct body and PDF attachments were added
        for part in message.walk():
            # multipart/* are just containers
            if part.get_content_type() == 'application/pdf':
                self.assertEqual(part.get_payload(decode=True), bytes)
                self.assertEqual(part.get_filename(), 'pdf-sample.pdf')
            elif part.get_content_type() == 'text/plain':
                body = '''Greetings CLARKE,

The Cyber Hygiene scan results are attached for your review. Same password as before. (If this is your first report and you have yet to receive a password, please let us know!)

If you have any questions, please contact our office.

Cheers,
The NCATS team

National Cybersecurity Assessments and Technical Services (NCATS)
National Cybersecurity and Communications Integration Center
U.S. Department of Homeland Security
ncats@hq.dhs.gov

WARNING: This document is FOR OFFICIAL USE ONLY (FOUO). It contains information that may be exempt from public release under the Freedom of Information Act (5 U.S.G. 552). It is to be controlled, stored, handled, transmitted, distributed, and disposed of in accordance with DHS policy relating to FOUO information and is not to be released to the public or other personnel who do not have a valid 'need-to-know' without prior approval of an authorized DHS official.
'''
                self.assertEqual(part.get_payload(), body)
            elif part.get_content_type() == 'text/html':
                html_body = '''<html>
<head></head>
<body>
<p>Greetings CLARKE,</p>

<p>The Cyber Hygiene scan results are attached for your review. Same password as before. (If this is your first report and you have yet to receive a password, please let us know!)</p>

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

    def test_six_params_multiple_cc(self):
        to = ['recipient@example.com', 'recipient2@example.com']
        pdf = './tests/data/pdf-sample.pdf'
        fm = 'sender@example.com'
        cc = ['cc@example.com', 'cc2@example.com']
        agency_acronym = 'CLARKE'
        report_date = 'December 15, 2001'

        message = CyhyMessage(to, pdf, agency_acronym, report_date, from_addr=fm, cc_addrs=cc)

        self.assertEqual(message['From'], fm)
        self.assertEqual(message['Subject'], 'CLARKE - Cyber Hygiene Report - December 15, 2001 Results')
        self.assertEqual(message['CC'], 'cc@example.com,cc2@example.com')
        self.assertEqual(message['To'], 'recipient@example.com,recipient2@example.com')

        # Grab the bytes that comprise the attachment
        bytes = open(pdf, 'rb').read()

        # Make sure the correct body and PDF attachments were added
        for part in message.walk():
            # multipart/* are just containers
            if part.get_content_type() == 'application/pdf':
                self.assertEqual(part.get_payload(decode=True), bytes)
                self.assertEqual(part.get_filename(), 'pdf-sample.pdf')
            elif part.get_content_type() == 'text/plain':
                body = '''Greetings CLARKE,

The Cyber Hygiene scan results are attached for your review. Same password as before. (If this is your first report and you have yet to receive a password, please let us know!)

If you have any questions, please contact our office.

Cheers,
The NCATS team

National Cybersecurity Assessments and Technical Services (NCATS)
National Cybersecurity and Communications Integration Center
U.S. Department of Homeland Security
ncats@hq.dhs.gov

WARNING: This document is FOR OFFICIAL USE ONLY (FOUO). It contains information that may be exempt from public release under the Freedom of Information Act (5 U.S.G. 552). It is to be controlled, stored, handled, transmitted, distributed, and disposed of in accordance with DHS policy relating to FOUO information and is not to be released to the public or other personnel who do not have a valid 'need-to-know' without prior approval of an authorized DHS official.
'''
                self.assertEqual(part.get_payload(), body)
            elif part.get_content_type() == 'text/html':
                html_body = '''<html>
<head></head>
<body>
<p>Greetings CLARKE,</p>

<p>The Cyber Hygiene scan results are attached for your review. Same password as before. (If this is your first report and you have yet to receive a password, please let us know!)</p>

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


if __name__ == '__main__':
    unittest.main()
