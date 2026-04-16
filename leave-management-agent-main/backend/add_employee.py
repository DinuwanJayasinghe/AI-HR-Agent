from agent.database import Database

# Initialize database
db = Database()

# Employee information
email = "kaveencdeshapriya@gmail.com"
name = "Kaveen C Deshapriya"
manager_email = "hr@company.com"  # You may need to update this

# Add employee to database
print(f"Adding employee: {name} ({email})")
db.add_employee(email, name, manager_email)
print("Employee added successfully!")

# Set leave balances
print("\nSetting leave balances...")

# Set vacation leave to 1 day
db.set_leave_balance(email, "Vacation", 1)
print(f"  - Vacation: 1 day")

# Set default leave balances for other types (you can adjust these)
db.set_leave_balance(email, "Sick Leave", 10)
print(f"  - Sick Leave: 10 days")

db.set_leave_balance(email, "Personal Leave", 5)
print(f"  - Personal Leave: 5 days")

print("\nEmployee setup complete!")

# Verify the employee was added
employee = db.get_employee(email)
print(f"\nVerification:")
print(f"  Name: {employee['name']}")
print(f"  Email: {employee['email']}")
print(f"  Manager: {employee['manager_email']}")
print(f"  Vacation Balance: {db.get_leave_balance(email, 'Vacation')} days")
