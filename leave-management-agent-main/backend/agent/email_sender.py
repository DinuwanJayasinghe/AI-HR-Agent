import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


class EmailSender:
    def __init__(self):
        self.email_address = os.getenv("EMAIL_ADDRESS")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "465"))

    def send_email(self, to_email: str, subject: str, html_body: str):
        msg = MIMEMultipart("alternative")
        msg["From"] = self.email_address
        msg["To"] = to_email
        msg["Subject"] = subject

        html_part = MIMEText(html_body, "html")
        msg.attach(html_part)

        with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
            server.login(self.email_address, self.email_password)
            server.send_message(msg)

    def send_hr_approval_request(self, hr_email: str, leave_details: dict):
        from agent.prompts import HR_REQUEST_EMAIL_TEMPLATE

        html_body = HR_REQUEST_EMAIL_TEMPLATE.format(**leave_details)
        subject = f"Leave Approval Required - {leave_details['employee_email']}"

        self.send_email(hr_email, subject, html_body)

    def send_approval_email(self, employee_email: str, details: dict):
        from agent.prompts import APPROVAL_EMAIL_TEMPLATE

        html_body = APPROVAL_EMAIL_TEMPLATE.format(**details)
        subject = "Leave Request Approved"

        self.send_email(employee_email, subject, html_body)

    def send_rejection_email(self, employee_email: str, details: dict):
        from agent.prompts import REJECTION_EMAIL_TEMPLATE

        html_body = REJECTION_EMAIL_TEMPLATE.format(**details)
        subject = "Leave Request Rejected"

        self.send_email(employee_email, subject, html_body)
