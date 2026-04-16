from fastapi import APIRouter, Query
from backend.core.database import SessionLocal
from backend.core.crud import calculate_payroll

router = APIRouter(prefix="/payroll", tags=["Payroll"])

@router.get("/calculate")
def calc(emp_id: str, month: int = Query(...), year: int = Query(...)):
    db = SessionLocal()
    data = calculate_payroll(db, emp_id, month, year)
    db.close()
    return data
