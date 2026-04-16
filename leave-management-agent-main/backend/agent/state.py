from typing import TypedDict, Optional


class LeaveState(TypedDict):
    raw_email: str
    employee_email: str
    leave_details: dict
    leave_type: str
    policy_decision: dict
    hr_decision: Optional[str]
    final_status: Optional[str]
    email_subject: str
    email_body: str
    email_from: str
