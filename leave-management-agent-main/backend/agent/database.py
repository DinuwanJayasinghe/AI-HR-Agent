import sqlite3
import os
from typing import Optional, Dict


class Database:
    def __init__(self, db_path: str = "data/employees.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                email TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                manager_email TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leave_balance (
                email TEXT,
                leave_type TEXT,
                balance INTEGER,
                PRIMARY KEY (email, leave_type),
                FOREIGN KEY (email) REFERENCES employees(email)
            )
        """)

        conn.commit()
        conn.close()

        self._seed_data()

    def _seed_data(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM employees")
        if cursor.fetchone()[0] == 0:
            sample_employees = [
                ("john.doe@company.com", "John Doe", "manager@company.com"),
                ("jane.smith@company.com", "Jane Smith", "manager@company.com"),
            ]
            cursor.executemany("INSERT INTO employees VALUES (?, ?, ?)", sample_employees)

            sample_balances = [
                ("john.doe@company.com", "Vacation", 15),
                ("john.doe@company.com", "Sick Leave", 10),
                ("john.doe@company.com", "Personal Leave", 5),
                ("jane.smith@company.com", "Vacation", 20),
                ("jane.smith@company.com", "Sick Leave", 10),
                ("jane.smith@company.com", "Personal Leave", 5),
            ]
            cursor.executemany("INSERT INTO leave_balance VALUES (?, ?, ?)", sample_balances)

            conn.commit()

        conn.close()

    def get_employee(self, email: str) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT email, name, manager_email FROM employees WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {"email": row[0], "name": row[1], "manager_email": row[2]}
        return None

    def get_leave_balance(self, email: str, leave_type: str) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT balance FROM leave_balance WHERE email = ? AND leave_type = ?",
            (email, leave_type)
        )
        row = cursor.fetchone()
        conn.close()

        return row[0] if row else 0

    def update_leave_balance(self, email: str, leave_type: str, days: int):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE leave_balance SET balance = balance - ? WHERE email = ? AND leave_type = ?",
            (days, email, leave_type)
        )
        conn.commit()
        conn.close()

    def add_employee(self, email: str, name: str, manager_email: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO employees VALUES (?, ?, ?)",
            (email, name, manager_email)
        )
        conn.commit()
        conn.close()

    def set_leave_balance(self, email: str, leave_type: str, balance: int):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO leave_balance VALUES (?, ?, ?)",
            (email, leave_type, balance)
        )
        conn.commit()
        conn.close()
