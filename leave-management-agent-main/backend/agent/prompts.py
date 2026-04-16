LEAVE_EXTRACTION_PROMPT = """
Extract leave request details from the following email and return ONLY valid JSON.

Email:
{email_content}

Return JSON with this exact structure:
{{
    "employee_email": "email@company.com",
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD",
    "days_requested": number,
    "reason": "brief reason"
}}

JSON:
"""

LEAVE_CATEGORIZATION_PROMPT = """
Categorize this leave request into ONE of these types:
- Vacation
- Sick Leave
- Maternity/Paternity
- Bereavement
- Personal Leave

Leave details:
{leave_details}

Return ONLY the category name, nothing else.
"""

POLICY_DECISION_PROMPT = """
Analyze this leave request against company policy and return ONLY valid JSON.

Leave Type: {leave_type}
Days Requested: {days_requested}
Current Balance: {balance}
Policy Rules: {policy_rules}

Decision logic:
- If balance insufficient: auto_reject
- If days exceed policy limit: needs_hr
- Otherwise: auto_approve

Return JSON:
{{
    "decision": "auto_approve|auto_reject|needs_hr",
    "explanation": "brief reason"
}}

JSON:
"""

HR_REQUEST_EMAIL_TEMPLATE = """
<html>
<body>
<h2>Leave Approval Required</h2>
<p><strong>Employee:</strong> {employee_email}</p>
<p><strong>Leave Type:</strong> {leave_type}</p>
<p><strong>Dates:</strong> {start_date} to {end_date}</p>
<p><strong>Days:</strong> {days_requested}</p>
<p><strong>Reason:</strong> {reason}</p>
<p><strong>Current Balance:</strong> {balance} days</p>

<p>Please reply with <strong>APPROVE</strong> or <strong>REJECT</strong></p>
</body>
</html>
"""

APPROVAL_EMAIL_TEMPLATE = """
<html>
<body>
<h2>Leave Request Approved</h2>
<p>Dear {employee_name},</p>
<p>Your leave request has been approved.</p>
<p><strong>Leave Type:</strong> {leave_type}</p>
<p><strong>Dates:</strong> {start_date} to {end_date}</p>
<p><strong>Days:</strong> {days_requested}</p>
<p><strong>Remaining Balance:</strong> {remaining_balance} days</p>
</body>
</html>
"""

REJECTION_EMAIL_TEMPLATE = """
<html>
<body>
<h2>Leave Request Rejected</h2>
<p>Dear {employee_name},</p>
<p>Your leave request has been rejected.</p>
<p><strong>Reason:</strong> {reason}</p>
<p><strong>Leave Type:</strong> {leave_type}</p>
<p><strong>Dates:</strong> {start_date} to {end_date}</p>
</body>
</html>
"""
