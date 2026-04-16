"""
Automatic CV Processor - Background Scheduler

This script automatically:
1. Checks Gmail for new CV/Resume emails every 5 minutes
2. Downloads new CVs to cv_collection folder
3. Sends acknowledgment emails to each CV sender
4. Logs all senders to CSV file
5. Analyzes CVs with ATS scoring

Run this script in the background to enable automatic CV processing.
"""

import os
import time
import schedule
from datetime import datetime
from dotenv import load_dotenv
from agent.tools.cv_review_tools import (
    get_gmail_credentials_oauth,
    create_cv_folder,
    download_cv_from_gmail,
    analyze_resume_ats,
    extract_text_from_pdf_file,
    extract_text_from_docx_file,
    save_individual_cv_analysis
)
from agent.tools.email_tools import log_cv_sender_to_csv, get_gmail_service, create_email_message
from googleapiclient.discovery import build
from langchain_google_genai import ChatGoogleGenerativeAI
import json

load_dotenv()


class CVAutoProcessor:
    def __init__(self, check_interval_minutes=5):
        """
        Initialize the automatic CV processor.

        Args:
            check_interval_minutes (int): How often to check for new CVs (default: 5 minutes)
        """
        self.check_interval = check_interval_minutes
        self.cv_folder = create_cv_folder()
        self.processed_cv_ids = set()  # Track already processed CVs
        self.load_processed_ids()

        print(f"✓ CV Auto Processor Initialized")
        print(f"✓ CV Folder: {self.cv_folder}")
        print(f"✓ Check Interval: Every {self.check_interval} minutes")
        print(f"✓ Monitoring: kaveencdeshapriya@gmail.com")
        print("-" * 60)

    def load_processed_ids(self):
        """Load previously processed CV IDs from file to avoid re-processing."""
        processed_ids_file = os.path.join(self.cv_folder, '.processed_cv_ids.txt')
        if os.path.exists(processed_ids_file):
            with open(processed_ids_file, 'r') as f:
                self.processed_cv_ids = set(line.strip() for line in f)
            print(f"✓ Loaded {len(self.processed_cv_ids)} previously processed CV IDs")

    def save_processed_id(self, cv_id):
        """Save a processed CV ID to file."""
        processed_ids_file = os.path.join(self.cv_folder, '.processed_cv_ids.txt')
        with open(processed_ids_file, 'a') as f:
            f.write(f"{cv_id}\n")
        self.processed_cv_ids.add(cv_id)

    def send_acknowledgment_email(self, sender_email, sender_name, cv_filename, date_sent):
        """Send acknowledgment email to CV sender."""
        try:
            gmail_service = get_gmail_service()
            from_email = "hr.agent.automation@gmail.com"

            subject = "Thank You for Your Application - CV Received"
            body = f"""Dear {sender_name},

Thank you for submitting your CV/Resume to our team.

We have successfully received your application and it is currently being reviewed by our HR department. Our team will carefully assess your qualifications and experience.

We will contact you as soon as possible regarding the next steps in the recruitment process. This typically takes 3-5 business days.

If you have any questions in the meantime, please feel free to reach out to us.

Thank you for your interest in joining our organization.

Best regards,
HR Department
{from_email}

---
This is an automated acknowledgment email. Please do not reply to this message.
"""

            email_message = create_email_message(from_email, sender_email, subject, body)
            gmail_service.users().messages().send(userId='me', body=email_message).execute()

            # Log to CSV
            log_cv_sender_to_csv({
                'name': sender_name,
                'email': sender_email,
                'cv_filename': cv_filename,
                'date_sent': date_sent,
                'reply_sent': 'Yes'
            }, self.cv_folder)

            return True
        except Exception as e:
            print(f"✗ Error sending acknowledgment to {sender_email}: {str(e)}")
            # Log failed attempt
            log_cv_sender_to_csv({
                'name': sender_name,
                'email': sender_email,
                'cv_filename': cv_filename,
                'date_sent': date_sent,
                'reply_sent': 'No'
            }, self.cv_folder)
            return False

    def process_new_cvs(self):
        """Main processing function - checks for and processes new CVs."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[{timestamp}] Checking for new CVs...")

        try:
            # Get Gmail credentials
            creds = get_gmail_credentials_oauth()
            gmail_service = build('gmail', 'v1', credentials=creds)

            # Download CVs
            downloaded_cvs = download_cv_from_gmail(gmail_service, self.cv_folder)

            if not downloaded_cvs:
                print("  → No new CVs found")
                return

            new_cvs = []
            for cv_info in downloaded_cvs:
                cv_id = cv_info.get('filepath', '')
                if cv_id not in self.processed_cv_ids:
                    new_cvs.append(cv_info)

            if not new_cvs:
                print("  → No new CVs to process (all already processed)")
                return

            print(f"  ✓ Found {len(new_cvs)} new CV(s)")

            # Initialize LLM for analysis
            llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3)

            # Process each new CV
            for idx, cv_info in enumerate(new_cvs, 1):
                try:
                    filename = cv_info['filename']
                    filepath = cv_info['filepath']
                    sender = cv_info['sender']
                    date = cv_info['date']

                    print(f"\n  [{idx}/{len(new_cvs)}] Processing: {filename}")
                    print(f"      From: {sender}")

                    # Extract sender email and name
                    sender_email = sender.split('<')[-1].replace('>', '').strip() if '<' in sender else sender
                    sender_name = sender.split('<')[0].strip() if '<' in sender else "Applicant"

                    # Send acknowledgment email
                    print(f"      → Sending acknowledgment email to {sender_email}...")
                    ack_sent = self.send_acknowledgment_email(sender_email, sender_name, filename, date)
                    if ack_sent:
                        print(f"      ✓ Acknowledgment email sent")
                    else:
                        print(f"      ✗ Failed to send acknowledgment email")

                    # Extract text from CV
                    print(f"      → Analyzing CV...")
                    if filepath.lower().endswith('.pdf'):
                        resume_text = extract_text_from_pdf_file(filepath)
                    elif filepath.lower().endswith(('.doc', '.docx')):
                        resume_text = extract_text_from_docx_file(filepath)
                    else:
                        print(f"      ✗ Unsupported file type")
                        continue

                    # Analyze with ATS
                    analysis = analyze_resume_ats(resume_text, llm, "")
                    ats_score = analysis.get("ats_score", 0)

                    # Save individual analysis
                    cv_info_for_save = {
                        'filename': filename,
                        'original_filename': cv_info['original_filename'],
                        'sender': sender,
                        'subject': cv_info['subject'],
                        'date': date,
                        'rank': 0  # Will be assigned later when comparing all CVs
                    }

                    analysis_file = save_individual_cv_analysis(cv_info_for_save, analysis, self.cv_folder)

                    print(f"      ✓ ATS Score: {ats_score}/100")
                    print(f"      ✓ Analysis saved: {os.path.basename(analysis_file) if analysis_file else 'Failed'}")

                    # Mark as processed
                    self.save_processed_id(filepath)

                    print(f"      ✓ CV processed successfully")

                except Exception as cv_error:
                    print(f"      ✗ Error processing CV: {str(cv_error)}")
                    continue

            print(f"\n✓ Batch complete: Processed {len(new_cvs)} new CV(s)")
            print(f"✓ Total CVs processed to date: {len(self.processed_cv_ids)}")

        except Exception as e:
            print(f"✗ Error in CV processing: {str(e)}")

    def start(self):
        """Start the automatic CV processor."""
        print("\n" + "=" * 60)
        print("CV AUTO PROCESSOR - STARTED")
        print("=" * 60)
        print(f"Monitoring Gmail: hr.agent.automation@gmail.com")
        print(f"Check interval: Every {self.check_interval} minutes")
        print(f"CV Folder: {self.cv_folder}")
        print(f"Press Ctrl+C to stop")
        print("=" * 60)

        # Schedule the job
        schedule.every(self.check_interval).minutes.do(self.process_new_cvs)

        # Run once immediately
        self.process_new_cvs()

        # Keep running
        try:
            while True:
                schedule.run_pending()
                time.sleep(30)  # Check every 30 seconds if any scheduled task needs to run
        except KeyboardInterrupt:
            print("\n\n" + "=" * 60)
            print("CV AUTO PROCESSOR - STOPPED")
            print("=" * 60)


def main():
    """Main entry point for the CV auto processor."""
    # You can customize the check interval here (in minutes)
    CHECK_INTERVAL_MINUTES = 5  # Check every 5 minutes

    processor = CVAutoProcessor(check_interval_minutes=CHECK_INTERVAL_MINUTES)
    processor.start()


if __name__ == "__main__":
    main()
