"""
CSV Tools - Tools for accessing and querying CSV data files
"""
from langchain_core.tools import tool
import os
import csv
import json


@tool
def read_cv_senders_log() -> str:
    """
    Reads the cv_senders_log.csv file that contains information about all CV senders.

    This CSV file contains:
    - Sender Name: Name of the person who sent the CV
    - Email: Email address of the sender
    - CV Filename: Name of the CV file received
    - Date Sent: When the CV was sent/received
    - Reply Sent: Whether acknowledgment email was sent (Yes/No)
    - Logged Date: When this entry was logged

    Returns:
        str: JSON string with all CV sender records
    """
    try:
        cv_folder = os.path.join(os.getcwd(), "cv_collection")
        csv_filepath = os.path.join(cv_folder, "cv_senders_log.csv")

        if not os.path.exists(csv_filepath):
            return json.dumps({
                "status": "error",
                "error": "cv_senders_log.csv does not exist yet. No CVs have been logged.",
                "total_records": 0,
                "records": []
            })

        records = []
        with open(csv_filepath, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                records.append({
                    "sender_name": row.get('Sender Name', 'Unknown'),
                    "email": row.get('Email', 'Unknown'),
                    "cv_filename": row.get('CV Filename', 'N/A'),
                    "date_sent": row.get('Date Sent', 'N/A'),
                    "reply_sent": row.get('Reply Sent', 'No'),
                    "logged_date": row.get('Logged Date', 'N/A')
                })

        result = {
            "status": "success",
            "csv_file": csv_filepath,
            "total_records": len(records),
            "records": records,
            "summary": f"Found {len(records)} CV sender records in the log"
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": f"Error reading CSV file: {str(e)}",
            "records": []
        })


@tool
def search_cv_senders(search_query: str = "", filter_by: str = "all") -> str:
    """
    Searches the cv_senders_log.csv file for specific CV senders.

    Args:
        search_query (str): Search term to look for (searches in name, email, filename)
        filter_by (str): Filter type - "all", "replied", "not_replied", "email", "name"

    Returns:
        str: JSON string with matching CV sender records
    """
    try:
        cv_folder = os.path.join(os.getcwd(), "cv_collection")
        csv_filepath = os.path.join(cv_folder, "cv_senders_log.csv")

        if not os.path.exists(csv_filepath):
            return json.dumps({
                "status": "error",
                "error": "cv_senders_log.csv does not exist yet",
                "total_matches": 0,
                "records": []
            })

        records = []
        with open(csv_filepath, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                record = {
                    "sender_name": row.get('Sender Name', 'Unknown'),
                    "email": row.get('Email', 'Unknown'),
                    "cv_filename": row.get('CV Filename', 'N/A'),
                    "date_sent": row.get('Date Sent', 'N/A'),
                    "reply_sent": row.get('Reply Sent', 'No'),
                    "logged_date": row.get('Logged Date', 'N/A')
                }

                # Apply filters
                if filter_by == "replied" and record["reply_sent"].lower() != "yes":
                    continue
                elif filter_by == "not_replied" and record["reply_sent"].lower() == "yes":
                    continue

                # Apply search query
                if search_query:
                    search_lower = search_query.lower()
                    if (search_lower in record["sender_name"].lower() or
                        search_lower in record["email"].lower() or
                        search_lower in record["cv_filename"].lower()):
                        records.append(record)
                else:
                    records.append(record)

        result = {
            "status": "success",
            "csv_file": csv_filepath,
            "search_query": search_query,
            "filter_by": filter_by,
            "total_matches": len(records),
            "records": records,
            "summary": f"Found {len(records)} matching CV sender records"
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": f"Error searching CSV file: {str(e)}",
            "records": []
        })


@tool
def get_cv_statistics() -> str:
    """
    Get statistics about CVs from the cv_senders_log.csv file.

    Returns:
        str: JSON string with statistics (total CVs, replied vs not replied, etc.)
    """
    try:
        cv_folder = os.path.join(os.getcwd(), "cv_collection")
        csv_filepath = os.path.join(cv_folder, "cv_senders_log.csv")

        if not os.path.exists(csv_filepath):
            return json.dumps({
                "status": "error",
                "error": "cv_senders_log.csv does not exist yet",
                "statistics": {}
            })

        total_cvs = 0
        replied_count = 0
        not_replied_count = 0
        unique_emails = set()

        with open(csv_filepath, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                total_cvs += 1
                email = row.get('Email', '')
                reply_status = row.get('Reply Sent', 'No')

                unique_emails.add(email)

                if reply_status.lower() == 'yes':
                    replied_count += 1
                else:
                    not_replied_count += 1

        statistics = {
            "total_cvs_received": total_cvs,
            "acknowledgments_sent": replied_count,
            "acknowledgments_pending": not_replied_count,
            "unique_senders": len(unique_emails),
            "reply_rate_percentage": round((replied_count / total_cvs * 100), 2) if total_cvs > 0 else 0
        }

        result = {
            "status": "success",
            "csv_file": csv_filepath,
            "statistics": statistics,
            "summary": f"Total CVs: {total_cvs}, Acknowledgments sent: {replied_count}, Pending: {not_replied_count}"
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": f"Error getting statistics: {str(e)}",
            "statistics": {}
        })


@tool
def list_downloaded_cvs() -> str:
    """
    Lists all CV files currently in the cv_collection folder.
    Shows CV filenames, file sizes, and modification dates.

    Returns:
        str: JSON string with list of all downloaded CV files
    """
    try:
        cv_folder = os.path.join(os.getcwd(), "cv_collection")

        if not os.path.exists(cv_folder):
            return json.dumps({
                "status": "error",
                "error": "cv_collection folder does not exist",
                "total_cvs": 0,
                "cv_files": []
            })

        cv_files = []
        all_files = os.listdir(cv_folder)

        # Filter only CV files (PDF, DOC, DOCX)
        for filename in all_files:
            if filename.lower().endswith(('.pdf', '.doc', '.docx')):
                filepath = os.path.join(cv_folder, filename)
                file_stats = os.stat(filepath)

                cv_files.append({
                    "filename": filename,
                    "filepath": filepath,
                    "size_kb": round(file_stats.st_size / 1024, 2),
                    "modified_date": file_stats.st_mtime
                })

        # Sort by modification date (newest first)
        cv_files.sort(key=lambda x: x['modified_date'], reverse=True)

        result = {
            "status": "success",
            "cv_folder": cv_folder,
            "total_cvs": len(cv_files),
            "cv_files": cv_files,
            "summary": f"Found {len(cv_files)} CV files in cv_collection folder"
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": f"Error listing CV files: {str(e)}",
            "cv_files": []
        })
