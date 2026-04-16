from langgraph.graph import StateGraph, END
from agent.state import LeaveState
from agent.database import Database
from agent.policy_engine import PolicyEngine
from agent.email_sender import EmailSender
from agent.hr_listener import HRListener
from agent.prompts import (
    LEAVE_EXTRACTION_PROMPT,
    LEAVE_CATEGORIZATION_PROMPT,
    POLICY_DECISION_PROMPT
)
from agent.utils import extract_json_from_text, clean_leave_type
import os
from openai import OpenAI


class LeaveManagementAgent:
    def __init__(self):
        self.db = Database()
        self.policy_engine = PolicyEngine()
        self.email_sender = EmailSender()
        self.hr_listener = HRListener()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.graph = self._build_graph()

    def _call_llm(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                timeout=60.0  # Increased timeout to 60 seconds
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"LLM API Error: {e}")
            raise

    def extract_leave_info(self, state: LeaveState) -> LeaveState:
        print("Extracting leave information...")

        # Get the sender's email from the state
        from_email = state.get("email_from", "")

        prompt = LEAVE_EXTRACTION_PROMPT.format(email_content=state["raw_email"])
        response = self._call_llm(prompt)

        leave_details = extract_json_from_text(response)

        # Override the employee_email with the actual sender's email
        # The LLM sometimes extracts placeholder emails, so we use the FROM field
        if from_email:
            leave_details["employee_email"] = from_email

        state["leave_details"] = leave_details
        state["employee_email"] = leave_details.get("employee_email", "")

        print(f"Extracted: {leave_details}")
        return state

    def validate_info(self, state: LeaveState) -> LeaveState:
        print("Validating information...")

        required_fields = ["employee_email", "start_date", "end_date", "days_requested", "reason"]
        missing = [f for f in required_fields if not state["leave_details"].get(f)]

        if missing:
            print(f"Missing fields: {missing}")
            state["final_status"] = "rejected"
            state["leave_details"]["rejection_reason"] = f"Missing required information: {', '.join(missing)}"

        return state

    def categorize_leave(self, state: LeaveState) -> LeaveState:
        print("Categorizing leave type...")

        prompt = LEAVE_CATEGORIZATION_PROMPT.format(
            leave_details=state["leave_details"]
        )
        response = self._call_llm(prompt)

        leave_type = clean_leave_type(response)
        state["leave_type"] = leave_type

        print(f"Category: {leave_type}")
        return state

    def check_policy(self, state: LeaveState) -> LeaveState:
        print("Checking policy...")

        days_requested = state["leave_details"]["days_requested"]
        balance = self.db.get_leave_balance(state["employee_email"], state["leave_type"])

        policy_decision = self.policy_engine.evaluate_leave_request(
            state["leave_type"],
            days_requested,
            balance
        )

        state["policy_decision"] = policy_decision
        state["leave_details"]["balance"] = balance

        print(f"Decision: {policy_decision['decision']} - {policy_decision['explanation']}")
        return state

    def route_decision(self, state: LeaveState) -> str:
        decision = state["policy_decision"]["decision"]

        if decision == "auto_approve":
            return "approve"
        elif decision == "auto_reject":
            return "reject"
        else:
            return "hr_approval"

    def request_hr_approval(self, state: LeaveState) -> LeaveState:
        print("Requesting HR approval...")

        hr_email = os.getenv("HR_EMAIL")

        self.email_sender.send_hr_approval_request(hr_email, state["leave_details"])

        print("HR approval email sent. Waiting for reply...")

        hr_decision = self.hr_listener.wait_for_hr_reply(state["employee_email"])

        if hr_decision:
            state["hr_decision"] = hr_decision
            print(f"HR Decision: {hr_decision}")
        else:
            state["hr_decision"] = "TIMEOUT"
            print("HR response timeout")

        return state

    def route_hr_decision(self, state: LeaveState) -> str:
        if state["hr_decision"] == "APPROVE":
            return "approve"
        else:
            return "reject"

    def approve_leave(self, state: LeaveState) -> LeaveState:
        print("Approving leave...")

        self.db.update_leave_balance(
            state["employee_email"],
            state["leave_type"],
            state["leave_details"]["days_requested"]
        )

        employee = self.db.get_employee(state["employee_email"])

        remaining_balance = self.db.get_leave_balance(
            state["employee_email"],
            state["leave_type"]
        )

        details = {
            **state["leave_details"],
            "employee_name": employee["name"],
            "leave_type": state["leave_type"],
            "remaining_balance": remaining_balance
        }

        self.email_sender.send_approval_email(state["employee_email"], details)

        state["final_status"] = "approved"

        print(f"Leave approved. Email sent to {state['employee_email']}")
        return state

    def reject_leave(self, state: LeaveState) -> LeaveState:
        print("Rejecting leave...")

        employee = self.db.get_employee(state["employee_email"])

        # If employee not found, use email as name
        employee_name = employee["name"] if employee else state["employee_email"]

        reason = state["leave_details"].get(
            "rejection_reason",
            state["policy_decision"].get("explanation", "Policy violation")
        )

        details = {
            **state["leave_details"],
            "employee_name": employee_name,
            "leave_type": state.get("leave_type", "Unknown"),
            "reason": reason
        }

        self.email_sender.send_rejection_email(state["employee_email"], details)

        state["final_status"] = "rejected"

        print(f"Rejection email sent to {state['employee_email']}")
        return state

    def should_continue_after_validation(self, state: LeaveState) -> str:
        if state.get("final_status") == "rejected":
            return "reject"
        return "continue"

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(LeaveState)

        workflow.add_node("extract_info", self.extract_leave_info)
        workflow.add_node("validate_info", self.validate_info)
        workflow.add_node("categorize_leave", self.categorize_leave)
        workflow.add_node("check_policy", self.check_policy)
        workflow.add_node("request_hr_approval", self.request_hr_approval)
        workflow.add_node("approve_leave", self.approve_leave)
        workflow.add_node("reject_leave", self.reject_leave)

        workflow.set_entry_point("extract_info")

        workflow.add_edge("extract_info", "validate_info")

        workflow.add_conditional_edges(
            "validate_info",
            self.should_continue_after_validation,
            {
                "continue": "categorize_leave",
                "reject": "reject_leave"
            }
        )

        workflow.add_edge("categorize_leave", "check_policy")

        workflow.add_conditional_edges(
            "check_policy",
            self.route_decision,
            {
                "approve": "approve_leave",
                "reject": "reject_leave",
                "hr_approval": "request_hr_approval"
            }
        )

        workflow.add_conditional_edges(
            "request_hr_approval",
            self.route_hr_decision,
            {
                "approve": "approve_leave",
                "reject": "reject_leave"
            }
        )

        workflow.add_edge("approve_leave", END)
        workflow.add_edge("reject_leave", END)

        return workflow.compile()

    def process_leave_request(self, email_data: dict):
        initial_state = LeaveState(
            raw_email=email_data["body"],
            employee_email="",
            leave_details={},
            leave_type="",
            policy_decision={},
            hr_decision=None,
            final_status=None,
            email_subject=email_data["subject"],
            email_body=email_data["body"],
            email_from=email_data.get("from", "")  # Add sender's email to state
        )

        print("\n" + "="*60)
        print(f"Processing leave request from: {email_data['from']}")
        print("="*60 + "\n")

        final_state = self.graph.invoke(initial_state)

        print("\n" + "="*60)
        print(f"Final Status: {final_state['final_status'].upper()}")
        print("="*60 + "\n")

        return final_state
