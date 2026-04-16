"""
CV Downloader Tool - Automatically downloads CVs from Gmail based on date range
"""
from langchain_core.tools import tool
import imaplib
import email
from email.header import decode_header
import os
from datetime import datetime, timedelta
import re
from dotenv import load_dotenv
import json

load_dotenv()


def sanitize_filename(filename):
    """Remove invalid characters from filename."""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)


def get_date_filter(days_back: int = 7):
    """Generate Gmail date filter for IMAP search.

    Args:
        days_back: Number of days to look back from today (default: 7)

    Returns:
        str: Date string in format for IMAP SINCE command
    """
    target_date = datetime.now() - timedelta(days=days_back)
    return target_date.strftime("%d-%b-%Y")


@tool
def download_cvs_from_gmail_by_date(days_back: int = 7, job_position: str = "") -> str:
    """
    Automatically downloads CV attachments from Gmail based on date range.
    Downloads CVs from emails received in the last N days.

    Args:
        days_back (int): Number of days to look back (default: 7 days)
        job_position (str): Optional job position to filter by subject line

    Returns:
        str: JSON string with download results and CV details

    Example:
        - download_cvs_from_gmail_by_date(7) - Downloads CVs from last 7 days
        - download_cvs_from_gmail_by_date(1, "R&D Engineer") - Downloads CVs from today for R&D Engineer
    """
    try:
        # Get credentials from .env
        email_address = os.getenv('EMAIL')
        password = os.getenv('EMAIL_PASSWORD')

        if not email_address or not password:
            return json.dumps({
                "status": "error",
                "error": "EMAIL and EMAIL_PASSWORD must be set in .env file"
            })

        # Create cv_collection folder
        cv_folder = os.path.join(os.getcwd(), "cv_collection")
        if not os.path.exists(cv_folder):
            os.makedirs(cv_folder)

        # Connect to Gmail IMAP server
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        imap.login(email_address, password)
        imap.select("INBOX")

        # Build search criteria based on date
        date_filter = get_date_filter(days_back)
        search_criteria = f'(SINCE {date_filter})'

        # Search for emails
        status, messages = imap.search(None, search_criteria)

        if status != "OK":
            return json.dumps({
                "status": "error",
                "error": "Failed to search emails"
            })

        email_ids = messages[0].split()
        downloaded_cvs = []
        processed_count = 0

        # Process each email
        for email_id in email_ids:
            try:
                # Fetch email
                status, msg_data = imap.fetch(email_id, "(RFC822)")

                if status != "OK":
                    continue

                # Parse email
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])

                        # Get email details
                        subject = decode_header(msg["Subject"])[0][0]
                        if isinstance(subject, bytes):
                            subject = subject.decode()

                        sender = msg.get("From", "")
                        date_received = msg.get("Date", "")

                        # Filter by job position if specified
                        if job_position and job_position.lower() not in subject.lower():
                            continue

                        # Check if email has attachments
                        if msg.is_multipart():
                            for part in msg.walk():
                                content_disposition = str(part.get("Content-Disposition", ""))

                                # Check if it's an attachment
                                if "attachment" in content_disposition:
                                    filename = part.get_filename()

                                    if filename:
                                        # Check if it's a CV file (PDF, DOC, DOCX)
                                        if filename.lower().endswith(('.pdf', '.doc', '.docx')):
                                            # Generate unique filename
                                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                            safe_filename = sanitize_filename(filename)
                                            unique_filename = f"{timestamp}_{safe_filename}"
                                            filepath = os.path.join(cv_folder, unique_filename)

                                            # Save attachment
                                            with open(filepath, "wb") as f:
                                                f.write(part.get_payload(decode=True))

                                            downloaded_cvs.append({
                                                "filename": unique_filename,
                                                "original_filename": filename,
                                                "filepath": filepath,
                                                "sender": sender,
                                                "subject": subject,
                                                "date_received": date_received
                                            })

                processed_count += 1

            except Exception as e:
                continue

        # Close connection
        imap.close()
        imap.logout()

        # Prepare result
        result = {
            "status": "success",
            "cv_folder": cv_folder,
            "days_back": days_back,
            "date_from": date_filter,
            "emails_processed": processed_count,
            "cvs_downloaded": len(downloaded_cvs),
            "job_position_filter": job_position if job_position else "None",
            "cv_details": downloaded_cvs,
            "summary": f"Successfully downloaded {len(downloaded_cvs)} CVs from the last {days_back} days (since {date_filter})"
        }

        return json.dumps(result, indent=2)

    except imaplib.IMAP4.error as e:
        return json.dumps({
            "status": "error",
            "error": f"Gmail login failed: {str(e)}. Make sure you're using an App Password."
        })
    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": f"Error downloading CVs: {str(e)}"
        })


@tool
def download_and_analyze_cvs(days_back: int = 7, job_description: str = "", job_position: str = "") -> str:
    """
    Complete workflow: Downloads CVs from Gmail by date AND analyzes them with AI.
    This is an all-in-one tool that combines downloading and analysis.

    Args:
        days_back (int): Number of days to look back (default: 7)
        job_description (str): Job description for better CV matching
        job_position (str): Job position to filter emails by subject

    Returns:
        str: JSON with download results and top 10 analyzed CVs with scores

    Example:
        "Download and analyze all CVs from last 3 days for R&D Engineer position"
    """
    from .cv_review_tools import collect_and_review_cvs_from_gmail

    try:
        # First, download CVs from Gmail by date
        download_result = download_cvs_from_gmail_by_date.invoke({
            "days_back": days_back,
            "job_position": job_position
        })

        download_data = json.loads(download_result)

        if download_data.get("status") == "error":
            return download_result

        # If no CVs downloaded, return early
        if download_data.get("cvs_downloaded", 0) == 0:
            return json.dumps({
                "status": "success",
                "message": f"No CVs found in the last {days_back} days",
                "download_summary": download_data
            })

        # Then analyze the downloaded CVs
        analysis_result = collect_and_review_cvs_from_gmail.invoke({
            "job_description": job_description
        })

        analysis_data = json.loads(analysis_result)

        # Combine results
        combined_result = {
            "status": "success",
            "download_summary": {
                "days_back": days_back,
                "date_from": download_data.get("date_from"),
                "emails_processed": download_data.get("emails_processed"),
                "cvs_downloaded": download_data.get("cvs_downloaded"),
                "job_position_filter": download_data.get("job_position_filter")
            },
            "analysis_summary": {
                "total_analyzed": analysis_data.get("total_resumes_analyzed", 0),
                "cv_folder": analysis_data.get("cv_folder")
            },
            "top_10_candidates": analysis_data.get("top_10_resumes", []),
            "summary": f"Downloaded {download_data.get('cvs_downloaded')} CVs from last {days_back} days and analyzed {analysis_data.get('total_resumes_analyzed', 0)} resumes. Top candidate score: {analysis_data.get('top_10_resumes', [{}])[0].get('ats_score', 0) if analysis_data.get('top_10_resumes') else 0}"
        }

        return json.dumps(combined_result, indent=2)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": f"Error in download and analyze workflow: {str(e)}"
        })
