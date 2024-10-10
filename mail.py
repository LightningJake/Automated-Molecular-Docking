import imaplib
import smtplib
import email
from email.mime.text import MIMEText
import time

EMAIL = 'chubchubjake@gmail.com'
PASSWORD = 'tffy jtcs dgkk fmyz'

IMAP_SERVER = 'imap.gmail.com'
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

def check_and_respond():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL, PASSWORD)
    mail.select('inbox')

    status, data = mail.search(None, 'UNSEEN')
    email_ids = data[0].split()

    for email_id in email_ids:
        status, data = mail.fetch(email_id, '(RFC822)')
        msg = email.message_from_bytes(data[0][1])
        from_ = email.utils.parseaddr(msg['From'])[1].lower()
        subject = msg['Subject']

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = msg.get_payload(decode=True).decode()

        lines = body.split('\n')
        name = surname = ''
        for line in lines:
            if line.startswith('name:'):
                name = line.split(':')[1].strip()
            elif line.startswith('surname:'):
                surname = line.split(':')[1].strip()

        response_message = f"Hello {name} {surname}"
        send_response(from_, response_message, subject)

    mail.logout()

def send_response(to, message, subject):
    msg = MIMEText(message)
    msg['Subject'] = f'Re: {subject}'
    msg['From'] = EMAIL
    msg['To'] = to

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.sendmail(EMAIL, to, msg.as_string())

while True:
    check_and_respond()
    time.sleep(30)

