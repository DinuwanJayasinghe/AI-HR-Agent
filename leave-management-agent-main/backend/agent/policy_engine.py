import json
import os


class PolicyEngine:
    def __init__(self, policy_file: str = "data/policies.json"):
        self.policy_file = policy_file
        self.policies = self._load_policies()

    def _load_policies(self) -> dict:
        if os.path.exists(self.policy_file):
            with open(self.policy_file, "r") as f:
                return json.load(f)
        else:
            default_policies = {
                "Vacation": {"max_days_without_hr": 5},
                "Sick Leave": {"max_days_without_hr": 3},
                "Maternity/Paternity": {"always_hr": True},
                "Bereavement": {"max_days": 5},
                "Personal Leave": {"max_days_without_hr": 2}
            }
            os.makedirs(os.path.dirname(self.policy_file), exist_ok=True)
            with open(self.policy_file, "w") as f:
                json.dump(default_policies, f, indent=2)
            return default_policies

    def get_policy(self, leave_type: str) -> dict:
        return self.policies.get(leave_type, {})

    def evaluate_leave_request(self, leave_type: str, days_requested: int, balance: int) -> dict:
        policy = self.get_policy(leave_type)

        if balance < days_requested:
            return {
                "decision": "auto_reject",
                "explanation": f"Insufficient balance. Requested: {days_requested}, Available: {balance}"
            }

        if policy.get("always_hr", False):
            return {
                "decision": "needs_hr",
                "explanation": f"{leave_type} always requires HR approval"
            }

        max_days = policy.get("max_days_without_hr", 0)

        if days_requested > max_days:
            return {
                "decision": "needs_hr",
                "explanation": f"Requested {days_requested} days exceeds auto-approval limit of {max_days} days"
            }

        return {
            "decision": "auto_approve",
            "explanation": f"Request within policy limits ({days_requested} <= {max_days} days) and sufficient balance"
        }
