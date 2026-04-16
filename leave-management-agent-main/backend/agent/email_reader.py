import imaplib
import email
from email.header import decode_header
from typing import List, Dict, Set
import os
import json


class EmailReader:
    def __init__(self):
        self.email_address = os.getenv("EMAIL_ADDRESS")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        self.imap_server = os.getenv("IMAP_SERVER", "imap.gmail.com")
        self.processed_file = "data/processed_emails.json"
        self.processed_emails: Set[str] = self._load_processed_emails()

    def _load_processed_emails(self) -> Set[str]:
        """Load previously processed email IDs from file"""
        if os.path.exists(self.processed_file):
            try:
                with open(self.processed_file, 'r') as f:
                    return set(json.load(f))
            except:
                return set()
        return set()

    def _save_processed_emails(self):
        """Save processed email IDs to file"""
        os.makedirs(os.path.dirname(self.processed_file), exist_ok=True)
        with open(self.processed_file, 'w') as f:
            json.dump(list(self.processed_emails), f)

    def connect(self) -> imaplib.IMAP4_SSL:
        mail = imaplib.IMAP4_SSL(self.imap_server)
        mail.login(self.email_address, self.email_password)
        return mail

    def read_unread_leave_requests(self) -> List[Dict]:
        mail = self.connect()
        mail.select("inbox")

        # Search for emails with "leave" in subject OR in body
        # This catches emails even if they have no subject line
        _, search_data1 = mail.search(None, 'SUBJECT "leave"')
        _, search_data2 = mail.search(None, 'BODY "leave"')

        # Combine both searches and remove duplicates
        email_ids = set(search_data1[0].split() + search_data2[0].split())

        leave_requests = []

        for num in email_ids:
            # Get email message
            _, msg_data = mail.fetch(num, "(RFC822)")
            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)

            # Create unique ID for this email
            message_id = email_message.get("Message-ID", "")
            email_date = email_message.get("Date", "")
            from_email = email.utils.parseaddr(email_message["From"])[1]

            # Skip system/automated emails
            if "no-reply" in from_email.lower() or "noreply" in from_email.lower():
                continue

            # Create a unique hash for this email
            email_hash = f"{message_id}_{from_email}_{email_date}"

            # Skip if already processed
            if email_hash in self.processed_emails:
                continue

            # Mark as processed
            self.processed_emails.add(email_hash)

            subject = self._decode_header(email_message["Subject"])
            body = self._get_email_body(email_message)

            print(f"Found new leave request from: {from_email}")
            print(f"Subject: {subject}")

            leave_requests.append({
                "subject": subject,
                "from": from_email,
                "body": body,
                "raw": email_message.as_string()
            })

        mail.close()
        mail.logout()

        # Save processed emails to disk
        if leave_requests:
            self._save_processed_emails()

        return leave_requests

    def _decode_header(self, header: str) -> str:
        if header is None:
            return ""
        decoded = decode_header(header)
        result = ""
        for content, encoding in decoded:
            if isinstance(content, bytes):
                result += content.decode(encoding or "utf-8")
            else:
                result += content
        return result

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

    def mark_as_read(self, email_from: str):
        pass
