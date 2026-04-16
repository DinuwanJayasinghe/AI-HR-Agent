from flask import Flask, jsonify, request
from flask_cors import CORS
from agent.database import Database
from datetime import datetime
import sqlite3

app = Flask(__name__)
CORS(app)

db = Database()


@app.route('/api/employees', methods=['GET'])
def get_employees():
    """Get all employees"""
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.email, e.name, e.manager_email,
               COALESCE(SUM(CASE WHEN lb.leave_type = 'Vacation' THEN lb.balance ELSE 0 END), 0) as vacation,
               COALESCE(SUM(CASE WHEN lb.leave_type = 'Sick Leave' THEN lb.balance ELSE 0 END), 0) as sick,
               COALESCE(SUM(CASE WHEN lb.leave_type = 'Personal Leave' THEN lb.balance ELSE 0 END), 0) as personal
        FROM employees e
        LEFT JOIN leave_balance lb ON e.email = lb.email
        GROUP BY e.email, e.name, e.manager_email
    """)
    employees = []
    for row in cursor.fetchall():
        employees.append({
            'email': row[0],
            'name': row[1],
            'manager_email': row[2],
            'leave_balance': {
                'Vacation': row[3],
                'Sick Leave': row[4],
                'Personal Leave': row[5]
            }
        })
    conn.close()
    return jsonify(employees)


@app.route('/api/employees/<email>', methods=['GET'])
def get_employee(email):
    """Get a specific employee"""
    employee = db.get_employee(email)
    if employee:
        leave_balance = {
            'Vacation': db.get_leave_balance(email, 'Vacation'),
            'Sick Leave': db.get_leave_balance(email, 'Sick Leave'),
            'Personal Leave': db.get_leave_balance(email, 'Personal Leave')
        }
        employee['leave_balance'] = leave_balance
        return jsonify(employee)
    return jsonify({'error': 'Employee not found'}), 404


@app.route('/api/employees', methods=['POST'])
def add_employee():
    """Add a new employee"""
    data = request.json
    try:
        db.add_employee(data['email'], data['name'], data.get('manager_email', ''))

        # Set default leave balances
        db.set_leave_balance(data['email'], 'Vacation', data.get('vacation', 15))
        db.set_leave_balance(data['email'], 'Sick Leave', data.get('sick_leave', 10))
        db.set_leave_balance(data['email'], 'Personal Leave', data.get('personal_leave', 5))

        return jsonify({'message': 'Employee added successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/leave-balance/<email>', methods=['GET'])
def get_leave_balance(email):
    """Get leave balance for an employee"""
    employee = db.get_employee(email)
    if not employee:
        return jsonify({'error': 'Employee not found'}), 404

    balance = {
        'employee': employee,
        'balances': {
            'Vacation': db.get_leave_balance(email, 'Vacation'),
            'Sick Leave': db.get_leave_balance(email, 'Sick Leave'),
            'Personal Leave': db.get_leave_balance(email, 'Personal Leave')
        }
    }
    return jsonify(balance)


@app.route('/api/leave-balance/<email>', methods=['PUT'])
def update_leave_balance(email):
    """Update leave balance for an employee"""
    data = request.json
    try:
        db.set_leave_balance(email, data['leave_type'], data['balance'])
        return jsonify({'message': 'Leave balance updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/leave-requests', methods=['GET'])
def get_leave_requests():
    """Get all leave requests (from processed emails)"""
    # This would read from a database table tracking all requests
    # For now, returning empty as the system processes emails in real-time
    return jsonify([])


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get dashboard statistics"""
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()

    # Count total employees
    cursor.execute("SELECT COUNT(*) FROM employees")
    total_employees = cursor.fetchone()[0]

    # Calculate total leave days across all employees
    cursor.execute("SELECT SUM(balance) FROM leave_balance")
    total_leave_days = cursor.fetchone()[0] or 0

    conn.close()

    return jsonify({
        'total_employees': total_employees,
        'total_leave_days': total_leave_days,
        'pending_requests': 0,  # Would be tracked in a requests table
        'approved_today': 0     # Would be tracked in a requests table
    })


if __name__ == '__main__':
    print("Starting Leave Management API Server...")
    print("API running on http://localhost:5000")
    app.run(debug=True, port=5000)
