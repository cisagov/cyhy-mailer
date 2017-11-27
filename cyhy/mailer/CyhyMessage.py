from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
import logging


class CyhyMessage(MIMEMultipart):

    DefaultFrom = 'ncats@hq.dhs.gov'

    DefaultCc = ['ncats@hq.dhs.gov']

    Subject = 'AGENCY_ACRONYM - CyHy - FY# Q# Results'

    Body = """Greetings AGENCY_ACRONYM,

The Cyber Hygiene scan results are attached for your review. Same password as before. (If this is your first report and you have yet to receive a password, please let us know!)

If you have any questions, please contact our office.

Cheers,
The NCATS team

National Cybersecurity Assessments and Technical Services (NCATS)
National Cybersecurity and Communications Integration Center
U.S. Department of Homeland Security
ncats@hq.dhs.gov

WARNING: This document is FOR OFFICIAL USE ONLY (FOUO). It contains information that may be exempt from public release under the Freedom of Information Act (5 U.S.G. 552). It is to be controlled, stored, handled, transmitted, distributed, and disposed of in accordance with DHS policy relating to FOUO information and is not to be released to the public or other personnel who do not have a valid 'need-to-know' without prior approval of an authorized DHS official.
"""

    def __init__(self, to_addrs, pdf_filename, from_addr=DefaultFrom, cc_addrs=DefaultCc):
        MIMEMultipart.__init__(self)

        self['From'] = from_addr
        logging.debug('Message to be sent from: %s', self['From'])

        self['To'] = ','.join(to_addrs)
        logging.debug('Message to be sent to: %s', self['To'])

        if cc_addrs:
            self['CC'] = ','.join(cc_addrs)
            logging.debug('Message sent as CC to: %s', self['CC'])

        self['Subject'] = CyhyMessage.Subject
        logging.debug('Message subject: %s', self['Subject'])

        self.attach(MIMEText(CyhyMessage.Body, 'plain'))
        logging.debug('Message body: %s', CyhyMessage.Body)

        attachment = open(pdf_filename, 'rb')
        part = MIMEBase('application', 'pdf')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename=%s' % pdf_filename)
        self.attach(part)
        logging.debug('Message PDF attachment: %s', pdf_filename)
