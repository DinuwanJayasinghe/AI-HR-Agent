import imaplib
import email
from typing import Optional
import os
import time


class HRListener:
    def __init__(self):
        self.email_address = os.getenv("EMAIL_ADDRESS")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        self.imap_server = os.getenv("IMAP_SERVER", "imap.gmail.com")
        self.hr_email = os.getenv("HR_EMAIL")

    def wait_for_hr_reply(self, employee_email: str, timeout: int = 300) -> Optional[str]:
        start_time = time.time()

        while time.time() - start_time < timeout:
            decision = self._check_for_reply(employee_email)
            if decision:
                return decision
            time.sleep(10)

        return None

    def _check_for_reply(self, employee_email: str) -> Optional[str]:
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.email_address, self.email_password)
            mail.select("inbox")

            _, search_data = mail.search(None, f'FROM "{self.hr_email}" UNSEEN')

            for num in search_data[0].split():
                _, msg_data = mail.fetch(num, "(RFC822)")
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)

                subject = str(email_message["Subject"])

                if employee_email in subject:
                    body = self._get_email_body(email_message)
                    decision = self._parse_decision(body)

                    if decision:
                        mail.close()
                        mail.logout()
                        return decision

            mail.close()
            mail.logout()
        except Exception as e:
            print(f"Error checking HR reply: {e}")

        return None

    def _get_email_body(self, email_message) -> str:
        body = ""
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                if content_type == "text/plain" and "attachment" not in content_disposition:
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = email_message.get_payload(decode=True).decode()

        return body

    def _parse_decision(self, body: str) -> Optional[str]:
        body_upper = body.upper()

        if "APPROVE" in body_upper:
            return "APPROVE"
        elif "REJECT" in body_upper:
            return "REJECT"

        return None
