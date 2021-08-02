from flask_mail import Mail, Message
from ssp.config import Config


class Emailer:
    recipients = Config.MAIL_DEFAULT_RCPT
    subject = "Default subject"
    html_file = '<h1>Hello World</h1>'

    def __init__(self, subject, html_file, rcpt_mail=0):
        self.subject = subject
        self.html_file = html_file
        if rcpt_mail != 0:
            self.recipients = rcpt_mail

    def send_mail(self, app, bcc=0):
        mail = Mail(app)
        msg = Message(self.subject, recipients=self.recipients) if bcc == 0 else Message(self.subject, recipients=self.recipients, bcc=bcc)
        msg.html = self.html_file
        mail.send(msg)
