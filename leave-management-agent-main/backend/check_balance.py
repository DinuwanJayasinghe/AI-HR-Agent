from agent.database import Database

db = Database()

email = input("Enter employee email: ")
employee = db.get_employee(email)

if employee:
    print(f"Employee: {employee['name']}")
    print(f"Email: {employee['email']}")
    print(f"\nLeave Balances:")
    print(f"  - Vacation: {db.get_leave_balance(email, 'Vacation')} days")
    print(f"  - Sick Leave: {db.get_leave_balance(email, 'Sick Leave')} days")
    print(f"  - Personal Leave: {db.get_leave_balance(email, 'Personal Leave')} days")
else:
    print(f"Employee with email {email} not found.")
