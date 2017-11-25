from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase


def create_message(from_addr, to_addrs, cc_addrs, subject, body_text, pdf_filename):
    message = MIMEMultipart()

    message['From'] = from_addr
    message['To'] = ','.join(to_addrs)
    if cc_addrs:
        message['CC'] = ','.join(cc_addrs)
    message['Subject'] = subject

    message.attach(MIMEText(body_text, 'plain'))

    attachment = open(pdf_filename, 'rb')
    part = MIMEBase('application', 'pdf')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename=%s' % pdf_filename)
    message.attach(part)

    return message


def send_message(smtp_server, message):
    smtp_server.send_message(message)
