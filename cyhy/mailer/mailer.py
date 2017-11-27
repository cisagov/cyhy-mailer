from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
import logging


def create_message(from_addr, to_addrs, cc_addrs, subject, body_text, pdf_filename):
    message = MIMEMultipart()

    message['From'] = from_addr
    logging.debug('Message to be sent from: %s', message['From'])
    message['To'] = ','.join(to_addrs)
    logging.debug('Message to be sent to: %s', message['To'])
    if cc_addrs:
        message['CC'] = ','.join(cc_addrs)
        logging.debug('Message sent as CC to: %s', message['CC'])
    message['Subject'] = subject
    logging.debug('Message subject: %s', message['Subject'])

    message.attach(MIMEText(body_text, 'plain'))
    logging.debug('Message body: %s', body_text)

    attachment = open(pdf_filename, 'rb')
    part = MIMEBase('application', 'pdf')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename=%s' % pdf_filename)
    message.attach(part)
    logging.debug('Message PDF attachment: %s', pdf_filename)

    return message


def send_message(smtp_server, message):
    smtp_server.send_message(message)
    logging.debug('Sent a message')
