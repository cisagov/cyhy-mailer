from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import logging

import pystache


class CyhyMessage(MIMEMultipart):
    """A class representing an email message with a CYHY report PDF
    attachment.

    Static attributes
    -----------------
    DefaultFrom : str
        The default value for the address from which the message
        should be sent.

    DefaultCc : str
        The default value for the CC addresses to which the message
        should be sent.

    Subject : str
        The mustache template to use when constructing the message
        subject.

    Body : str
        The mustache template to use when constriucting the message
        body.
    """

    DefaultFrom = 'ncats@hq.dhs.gov'

    DefaultCc = ['ncats@hq.dhs.gov']

    Subject = '{{acronym}} - CyHy - FY{{financial_year}} Q{{quarter}} Results'

    Body = """Greetings {{acronym}},

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

    def __init__(self, to_addrs, pdf_filename, agency_acronym, financial_year, fy_quarter, from_addr=DefaultFrom, cc_addrs=DefaultCc):
        """Construct an instance.

        Parameters
        ----------
        to_addrs : array of str
            An array of string objects, each of which is an email
            address to which this message should be sent.

        pdf_filename : str
            The filename of the PDF file that is teh CYHY report
            corresponding to this message.

        agency_acronym : str
            The acronym ised by the agency corresponding to the CYHY
            report attachment.

        financial_year : str
            The four-digit financial year to corresponding to the CYHY
            report attachment.

        fy_quarter : str
            The quarter of the financial year corresponding to the
            CYHY report attachment.

        from_addr : str
            The email address from which this message is to be sent.

        cc_addrs : array of str
            An array of string objects, each of which is a CC email
            address to which this message should be sent.
        """
        MIMEMultipart.__init__(self)

        self['From'] = from_addr
        logging.debug('Message to be sent from: %s', self['From'])

        self['To'] = ','.join(to_addrs)
        logging.debug('Message to be sent to: %s', self['To'])

        if cc_addrs:
            self['CC'] = ','.join(cc_addrs)
            logging.debug('Message to be sent as CC to: %s', self['CC'])

        # This is the data mustache will use to render the templates
        mustache_data = {
            'acronym': agency_acronym,
            'financial_year': financial_year,
            'quarter': fy_quarter
        }
        self['Subject'] = pystache.render(CyhyMessage.Subject, mustache_data)
        logging.debug('Message subject: %s', self['Subject'])

        body = pystache.render(CyhyMessage.Body, mustache_data)
        self.attach(MIMEText(body, 'plain'))
        logging.debug('Message body: %s', body)

        attachment = open(pdf_filename, 'rb')
        part = MIMEApplication(attachment.read(), 'pdf')
        encoders.encode_base64(part)
        # See https://en.wikipedia.org/wiki/MIME#Content-Disposition
        part.add_header('Content-Disposition', 'attachment; filename=%s' % pdf_filename)
        self.attach(part)
        logging.debug('Message PDF attachment: %s', pdf_filename)
