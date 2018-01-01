from email import encoders
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import os.path


class Message(MIMEMultipart):
    """A class representing an email message sent from the NCATS inbox.

    Static attributes
    -----------------
    DefaultFrom : str
        The default value for the address from which the message
        should be sent.

    DefaultCc : list of str
        The default value for the CC addresses to which the message
        should be sent.
    """

    DefaultFrom = 'ncats@hq.dhs.gov'

    DefaultCc = ['ncats@hq.dhs.gov']

    def __init__(self, to_addrs, subject=None, text_body=None, html_body=None, from_addr=DefaultFrom, cc_addrs=DefaultCc):
        """Construct an instance.

        Parameters
        ----------
        to_addrs : array of str
            An array of string objects, each of which is an email
            address to which this message should be sent.

        subject : str
            The subject of this email message.

        text_body : str
            The plain-text version of the email body.

        html_body : str
            The HTML version of the email body.

        from_addr : str
            The email address from which this message is to be sent.

        cc_addrs : array of str
            An array of string objects, each of which is a CC email
            address to which this message should be sent.
        """
        MIMEMultipart.__init__(self, 'alternative')

        self['From'] = from_addr
        logging.debug('Message to be sent from: %s', self['From'])

        self['To'] = ','.join(to_addrs)
        logging.debug('Message to be sent to: %s', self['To'])

        if cc_addrs:
            self['CC'] = ','.join(cc_addrs)
            logging.debug('Message to be sent as CC to: %s', self['CC'])

        if subject:
            self['Subject'] = subject
            logging.debug('Message subject: %s', subject)

        #
        # The order is important here.  This order makes the HTML
        # version the default version that is displayed, as long as
        # the client supports it.
        #
        if text_body:
            self.attach_text_body(text_body)

        if html_body:
            self.attach_html_body(html_body)

    def attach_text_body(self, text):
        """Attach a plain text body to this message.

        Parameters
        ----------
        text : str
            The plain text to attach.
        """
        self.attach(MIMEText(text, 'plain'))
        logging.debug('Message plain-text body: %s', text)

    def attach_html_body(self, html):
        """Attach an HTML text body to this message.

        Parameters
        ----------
        html : str
            The HTML text to attach.
        """
        part = MIMEText(html, 'html')
        part.add_header('Content-Disposition', 'inline')
        self.attach(part)
        logging.debug('Message HTML body: %s', html)

    def attach_pdf(self, pdf_filename):
        """Attach a PDF file to this message.

        Parameters
        ----------
        pdf_filename : str
            The filename of the PDF file to attach.
        """
        attachment = open(pdf_filename, 'rb')
        part = MIMEApplication(attachment.read(), 'pdf')
        encoders.encode_base64(part)
        # See https://en.wikipedia.org/wiki/MIME#Content-Disposition
        _, filename = os.path.split(pdf_filename)
        part.add_header('Content-Disposition', 'attachment', filename=filename)
        self.attach(part)
        logging.debug('Message PDF attachment: %s', pdf_filename)

    def attach_csv(self, csv_filename):
        """Attach a CSV file to this message.

        Parameters
        ----------
        csv_filename : str
            The filename of the CSV file to attach.
        """
        attachment = open(csv_filename, 'rb')
        part = MIMEText(attachment.read(), 'csv')
        # See https://en.wikipedia.org/wiki/MIME#Content-Disposition
        _, filename = os.path.split(csv_filename)
        part.add_header('Content-Disposition', 'attachment', filename=filename)
        self.attach(part)
        logging.debug('Message CSV attachment: %s', csv_filename)
