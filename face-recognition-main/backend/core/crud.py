from backend.core.models import Employee, AttendanceLog, LeaveRecord, FaceEncoding
from sqlalchemy.orm import Session
import datetime as dt, pickle
from backend.core.config import TIMEZONE

def create_employee(db: Session, emp_id, name, dept, position, salary, photo_bytes):
    emp = Employee(id=emp_id, name=name, department=dept, position=position, salary=salary, photo=photo_bytes)
    db.add(emp); db.commit(); db.refresh(emp)
    return emp

def add_face_encoding(db: Session, emp_id, enc):
    blob = pickle.dumps(enc)
    db.add(FaceEncoding(employee_id=emp_id, encoding=blob)); db.commit()

def mark_attendance(db: Session, emp_id, snapshot_bytes, latitude=None, longitude=None):
    """
    Mark attendance for an employee within a 24-hour cycle (00:00 - 23:59).
    - First detection of the day = Check-in (login) with GPS location
    - Second detection of the day = Check-out (logout) with GPS location
    - Work hours = logout time - login time (within same day)
    - Resets at midnight (00:00) for new day
    """
    now = dt.datetime.now(TIMEZONE)
    today = now.date()

    # Find today's attendance log for this employee
    log = db.query(AttendanceLog).filter_by(employee_id=emp_id, date=today).first()

    if not log:
        # First face detection today = CHECK-IN (Login)
        log = AttendanceLog(
            employee_id=emp_id,
            date=today,
            check_in=now,
            snapshot=snapshot_bytes,
            check_in_latitude=latitude,
            check_in_longitude=longitude,
            work_hours=0.0,
            overtime_hours=0.0
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    elif log.check_out is None:
        # Second face detection today = CHECK-OUT (Logout)
        log.check_out = now
        log.check_out_latitude = latitude
        log.check_out_longitude = longitude

        # Ensure check_in is timezone-aware for calculation
        check_in = log.check_in
        if check_in.tzinfo is None:
            check_in = TIMEZONE.localize(check_in)

        # Calculate working hours (logout - login) within the same day
        time_diff = (log.check_out - check_in).total_seconds()

        # Validate: check_out must be after check_in
        if time_diff < 0:
            # Invalid: checkout before checkin shouldn't happen
            log.work_hours = 0.0
            log.overtime_hours = 0.0
        else:
            # Calculate hours worked
            hours_worked = time_diff / 3600
            log.work_hours = round(hours_worked, 2)

            # Calculate overtime (anything over 8 hours)
            log.overtime_hours = round(max(0, log.work_hours - 8), 2)

        log.snapshot = snapshot_bytes
        db.commit()
        db.refresh(log)
        return log

    else:
        # Already checked in AND checked out today
        # Update the checkout time and recalculate (allows multiple checkouts)
        log.check_out = now
        log.check_out_latitude = latitude
        log.check_out_longitude = longitude

        # Ensure check_in is timezone-aware for calculation
        check_in = log.check_in
        if check_in.tzinfo is None:
            check_in = TIMEZONE.localize(check_in)

        # Recalculate working hours
        time_diff = (log.check_out - check_in).total_seconds()

        if time_diff < 0:
            log.work_hours = 0.0
            log.overtime_hours = 0.0
        else:
            hours_worked = time_diff / 3600
            log.work_hours = round(hours_worked, 2)
            log.overtime_hours = round(max(0, log.work_hours - 8), 2)

        log.snapshot = snapshot_bytes
        db.commit()
        db.refresh(log)
        return log

def add_leave(db: Session, emp_id, date, reason, type):
    leave = LeaveRecord(employee_id=emp_id, date=date, reason=reason, type=type)
    db.add(leave); db.commit(); db.refresh(leave)
    return leave

def calculate_payroll(db: Session, emp_id, month, year):
    emp = db.query(Employee).filter_by(id=emp_id).first()
    if not emp: return None
    logs = db.query(AttendanceLog).filter(
        AttendanceLog.employee_id==emp_id,
        AttendanceLog.date.between(dt.date(year, month, 1), dt.date(year, month, 28))
    ).all()
    total_hours = sum(r.work_hours or 0 for r in logs)
    total_ot = sum(r.overtime_hours or 0 for r in logs)
    leaves = db.query(LeaveRecord).filter_by(employee_id=emp_id, approved=1).count()
    base_salary = emp.salary or 0
    daily_rate = base_salary / 30
    leave_deduction = leaves * daily_rate
    ot_pay = total_ot * (daily_rate / 8 * 1.5)
    total_salary = base_salary - leave_deduction + ot_pay
    return {
        "employee_id": emp_id,
        "name": emp.name,
        "month": month,
        "year": year,
        "total_hours": total_hours,
        "overtime_hours": total_ot,
        "leaves": leaves,
        "final_salary": round(total_salary, 2)
    }
