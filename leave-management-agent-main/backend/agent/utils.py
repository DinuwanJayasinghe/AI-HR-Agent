import json
import re


def extract_json_from_text(text: str) -> dict:
    text = text.strip()

    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}


def clean_leave_type(leave_type: str) -> str:
    leave_type = leave_type.strip().title()
    valid_types = ["Vacation", "Sick Leave", "Maternity/Paternity", "Bereavement", "Personal Leave"]

    for valid_type in valid_types:
        if valid_type.lower() in leave_type.lower():
            return valid_type

    return leave_type
