from agent.graph import LeaveManagementAgent
from agent.email_reader import EmailReader
from dotenv import load_dotenv
import time


def main():
    load_dotenv()

    print("Leave Management Agent Starting...")
    print("=" * 60)

    agent = LeaveManagementAgent()
    email_reader = EmailReader()

    print("Agent initialized")
    print("Monitoring inbox for leave requests...\n")

    while True:
        try:
            leave_requests = email_reader.read_unread_leave_requests()

            if leave_requests:
                print(f"Found {len(leave_requests)} new leave request(s)\n")

                for request in leave_requests:
                    agent.process_leave_request(request)

            else:
                print("No new leave requests. Checking again in 30 seconds...")

            time.sleep(30)

        except KeyboardInterrupt:
            print("\n\nAgent stopped by user")
            break
        except Exception as e:
            print(f"\nError: {e}")
            print("Retrying in 30 seconds...\n")
            time.sleep(30)


if __name__ == "__main__":
    main()
