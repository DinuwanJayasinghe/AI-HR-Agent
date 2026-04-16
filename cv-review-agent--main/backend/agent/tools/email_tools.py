from langchain_core.tools import tool
import os
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import csv
from datetime import datetime


def get_gmail_service():
    """Get Gmail API service with OAuth2 authentication."""
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send'
    ]
    creds = None

    # Token file stores the user's access and refresh tokens
    token_file = 'token.pickle'

    # Check if token file exists
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)

    # If there are no valid credentials, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)


def create_email_message(sender_email, to_email, subject, body):
    """Create an email message."""
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = to_email
    message['Subject'] = subject

    message.attach(MIMEText(body, 'plain'))

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    return {'raw': raw_message}


def log_cv_sender_to_csv(cv_sender_info, cv_folder):
    """
    Log CV sender information to a CSV file in the cv_collection folder.

    Args:
        cv_sender_info (dict): Dictionary containing sender information
            - name: Sender name
            - email: Sender email
            - cv_filename: CV filename
            - date_sent: Date CV was sent
            - reply_sent: Whether acknowledgment email was sent (Yes/No)
        cv_folder (str): Path to cv_collection folder

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        csv_filepath = os.path.join(cv_folder, "cv_senders_log.csv")

        # Check if CSV file exists to determine if we need to write headers
        file_exists = os.path.exists(csv_filepath)

        # Open CSV file in append mode
        with open(csv_filepath, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Sender Name', 'Email', 'CV Filename', 'Date Sent', 'Reply Sent', 'Logged Date']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write header if file is new
            if not file_exists:
                writer.writeheader()

            # Write sender information
            writer.writerow({
                'Sender Name': cv_sender_info.get('name', 'Unknown'),
                'Email': cv_sender_info.get('email', 'Unknown'),
                'CV Filename': cv_sender_info.get('cv_filename', 'N/A'),
                'Date Sent': cv_sender_info.get('date_sent', 'N/A'),
                'Reply Sent': cv_sender_info.get('reply_sent', 'No'),
                'Logged Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        return True
    except Exception as e:
        print(f"Error logging to CSV: {str(e)}")
        return False


@tool
def send_cv_acknowledgment_email(recipient_email: str, recipient_name: str = "Applicant", cv_filename: str = "N/A", date_sent: str = "N/A"):
    """
    Sends an automatic acknowledgment email to a CV/Resume sender confirming receipt.
    Also logs the sender information to a CSV file in cv_collection folder.

    This tool is used when someone sends their CV/Resume to hr.agent.automation@gmail.com.
    It sends a professional acknowledgment email from hr.agent.automation@gmail.com.

    Args:
        recipient_email (str): The email address of the CV sender
        recipient_name (str): The name of the applicant (default: "Applicant")
        cv_filename (str): The filename of the CV (optional)
        date_sent (str): The date the CV was sent (optional)

    Returns:
        str: Success or error message
    """
    try:
        load_dotenv()

        # Sender email (your Gmail account)
        sender_email = "hr.agent.automation@gmail.com"

        # Email content
        subject = "Thank You for Your Application - CV Received"

        body = f"""Dear {recipient_name},

Thank you for submitting your CV/Resume to our team.

We have successfully received your application and it is currently being reviewed by our HR department. Our team will carefully assess your qualifications and experience.

We will contact you as soon as possible regarding the next steps in the recruitment process. This typically takes 3-5 business days.

If you have any questions in the meantime, please feel free to reach out to us.

Thank you for your interest in joining our organization.

Best regards,
HR Department
{sender_email}

---
This is an automated acknowledgment email. Please do not reply to this message.
"""

        # Get Gmail service
        gmail_service = get_gmail_service()

        # Create and send email
        email_message = create_email_message(sender_email, recipient_email, subject, body)

        gmail_service.users().messages().send(
            userId='me',
            body=email_message
        ).execute()

        # Log to CSV file
        cv_folder = os.path.join(os.getcwd(), "cv_collection")
        if not os.path.exists(cv_folder):
            os.makedirs(cv_folder)

        cv_sender_info = {
            'name': recipient_name,
            'email': recipient_email,
            'cv_filename': cv_filename,
            'date_sent': date_sent,
            'reply_sent': 'Yes'
        }

        log_cv_sender_to_csv(cv_sender_info, cv_folder)

        return f"✓ Acknowledgment email successfully sent to {recipient_email} ({recipient_name})\n✓ Logged to cv_senders_log.csv"

    except Exception as e:
        # Even if email fails, try to log with reply_sent = 'No'
        try:
            cv_folder = os.path.join(os.getcwd(), "cv_collection")
            if not os.path.exists(cv_folder):
                os.makedirs(cv_folder)

            cv_sender_info = {
                'name': recipient_name,
                'email': recipient_email,
                'cv_filename': cv_filename,
                'date_sent': date_sent,
                'reply_sent': 'No'
            }
            log_cv_sender_to_csv(cv_sender_info, cv_folder)
        except:
            pass

        return f"✗ Error sending acknowledgment email: {str(e)}"


@tool
def send_bulk_cv_acknowledgments(cv_senders: list):
    """
    Sends acknowledgment emails to multiple CV senders at once.
    Also logs each sender to the CSV file in cv_collection folder.

    This tool is useful after downloading multiple CVs from Gmail.
    It sends a professional acknowledgment to each CV sender.

    Args:
        cv_senders (list): List of dicts with keys: 'email', 'name', 'cv_filename', 'date_sent'
                          Example: [{'email': 'john@example.com', 'name': 'John Doe',
                                    'cv_filename': 'john_cv.pdf', 'date_sent': '2025-12-26'}]

    Returns:
        str: Summary of sent emails (success/failure counts)
    """
    try:
        load_dotenv()

        if not cv_senders:
            return "No CV senders provided"

        # Get Gmail service once for all emails
        gmail_service = get_gmail_service()
        sender_email = "hr.agent.automation@gmail.com"

        # Get CV folder for logging
        cv_folder = os.path.join(os.getcwd(), "cv_collection")
        if not os.path.exists(cv_folder):
            os.makedirs(cv_folder)

        success_count = 0
        failed_count = 0
        results = []

        for sender_info in cv_senders:
            try:
                recipient_email = sender_info.get('email', '')
                recipient_name = sender_info.get('name', 'Applicant')
                cv_filename = sender_info.get('cv_filename', 'N/A')
                date_sent = sender_info.get('date_sent', 'N/A')

                if not recipient_email:
                    failed_count += 1
                    # Log failed entry
                    log_cv_sender_to_csv({
                        'name': recipient_name,
                        'email': 'No email provided',
                        'cv_filename': cv_filename,
                        'date_sent': date_sent,
                        'reply_sent': 'No'
                    }, cv_folder)
                    continue

                # Email content
                subject = "Thank You for Your Application - CV Received"

                body = f"""Dear {recipient_name},

Thank you for submitting your CV/Resume to our team.

We have successfully received your application and it is currently being reviewed by our HR department. Our team will carefully assess your qualifications and experience.

We will contact you as soon as possible regarding the next steps in the recruitment process. This typically takes 3-5 business days.

If you have any questions in the meantime, please feel free to reach out to us.

Thank you for your interest in joining our organization.

Best regards,
HR Department
{sender_email}

---
This is an automated acknowledgment email. Please do not reply to this message.
"""

                # Create and send email
                email_message = create_email_message(sender_email, recipient_email, subject, body)

                gmail_service.users().messages().send(
                    userId='me',
                    body=email_message
                ).execute()

                success_count += 1
                results.append(f"✓ Sent to {recipient_email}")

                # Log successful send
                log_cv_sender_to_csv({
                    'name': recipient_name,
                    'email': recipient_email,
                    'cv_filename': cv_filename,
                    'date_sent': date_sent,
                    'reply_sent': 'Yes'
                }, cv_folder)

            except Exception as sender_error:
                failed_count += 1
                results.append(f"✗ Failed to send to {recipient_email}: {str(sender_error)}")

                # Log failed send
                log_cv_sender_to_csv({
                    'name': sender_info.get('name', 'Applicant'),
                    'email': sender_info.get('email', 'Unknown'),
                    'cv_filename': sender_info.get('cv_filename', 'N/A'),
                    'date_sent': sender_info.get('date_sent', 'N/A'),
                    'reply_sent': 'No'
                }, cv_folder)

        summary = f"\n\nAcknowledgment Email Summary:\n"
        summary += f"✓ Successfully sent: {success_count}\n"
        summary += f"✗ Failed: {failed_count}\n"
        summary += f"✓ All entries logged to cv_senders_log.csv\n"
        summary += f"\nDetails:\n" + "\n".join(results)

        return summary

    except Exception as e:
        return f"✗ Error sending bulk acknowledgment emails: {str(e)}"
