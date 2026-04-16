from fastapi import APIRouter, Form
from backend.core.database import SessionLocal
from backend.core.models import LeaveRecord
from datetime import date

router = APIRouter(prefix="/leave", tags=["Leave"])

@router.post("/")
def request_leave(
    employee_id: str = Form(...),
    leave_date: str = Form(...),
    reason: str = Form(None),
    leave_type: str = Form(None)
):
    db = SessionLocal()
    leave = LeaveRecord(
        employee_id=employee_id,
        date=date.fromisoformat(leave_date),
        reason=reason,
        type=leave_type,
        approved=0
    )
    db.add(leave)
    db.commit()
    db.close()
    return {"message": "Leave request submitted"}

@router.get("/")
def get_leaves(employee_id: str = None):
    db = SessionLocal()
    if employee_id:
        leaves = db.query(LeaveRecord).filter(LeaveRecord.employee_id == employee_id).all()
    else:
        leaves = db.query(LeaveRecord).all()

    res = [{
        "id": leave.id,
        "employee_id": leave.employee_id,
        "date": str(leave.date),
        "reason": leave.reason,
        "type": leave.type,
        "approved": leave.approved
    } for leave in leaves]
    db.close()
    return res

@router.put("/{leave_id}/approve")
def approve_leave(leave_id: int):
    db = SessionLocal()
    leave = db.query(LeaveRecord).filter(LeaveRecord.id == leave_id).first()
    if leave:
        leave.approved = 1
        db.commit()
        db.close()
        return {"message": "Leave approved"}
    db.close()
    return {"error": "Leave not found"}
