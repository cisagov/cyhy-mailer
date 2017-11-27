import logging


def send_message(smtp_server, message):
    smtp_server.send_message(message)
    logging.debug('Sent a message')
