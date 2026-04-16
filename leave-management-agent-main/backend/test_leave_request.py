from agent.graph import LeaveManagementAgent
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Check if OpenAI API key is set
api_key = os.getenv("OPENAI_API_KEY")
if not api_key or api_key == "sk-your-openai-api-key":
    print("ERROR: OPENAI_API_KEY is not properly set in .env file")
    print("Please update your .env file with a valid OpenAI API key")
    exit(1)

print("OpenAI API Key is configured")
print(f"Key starts with: {api_key[:10]}...")

# Create a test leave request
test_request = {
    "from": "kaveencdeshapriya@gmail.com",
    "subject": "06/01 leave asked from the company",
    "body": """
    Hi,

    I would like to request leave on 06/01/2026 (1 day).

    Reason: Personal matter

    Thank you,
    Kaveen C Deshapriya
    """
}

print("\nInitializing Leave Management Agent...")
agent = LeaveManagementAgent()

print("\nProcessing test leave request...")
print("=" * 60)

try:
    result = agent.process_leave_request(test_request)
    print("\nTest completed successfully!")
    print(f"Final status: {result['final_status']}")
except Exception as e:
    print(f"\nError during processing: {e}")
    import traceback
    traceback.print_exc()
