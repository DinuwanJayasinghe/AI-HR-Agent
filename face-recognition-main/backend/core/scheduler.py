from apscheduler.schedulers.background import BackgroundScheduler
import datetime as dt
from backend.core.config import TIMEZONE
from backend.core.database import SessionLocal
from backend.core.models import AttendanceLog

def finalize_sessions():
    """Mark employees as logged out if inactive."""
    db = SessionLocal()
    cutoff = dt.datetime.now(TIMEZONE) - dt.timedelta(minutes=10)
    logs = db.query(AttendanceLog).filter(AttendanceLog.check_out == None).all()
    for log in logs:
        # Ensure check_in is timezone-aware for comparison
        check_in = log.check_in
        if check_in.tzinfo is None:
            check_in = TIMEZONE.localize(check_in)

        if check_in < cutoff:
            log.check_out = cutoff
            log.work_hours = (log.check_out - check_in).total_seconds() / 3600
            log.overtime_hours = max(0, log.work_hours - 8)
    db.commit()
    db.close()

def start_scheduler():
    scheduler = BackgroundScheduler(timezone=str(TIMEZONE))
    scheduler.add_job(finalize_sessions, "interval", minutes=5)
    scheduler.start()
    print("🕒 Scheduler started (runs every 5 min).")
