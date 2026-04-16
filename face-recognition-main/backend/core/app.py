from fastapi import FastAPI
from backend.routers import employee, attendance, payroll, leave
from backend.core.database import init_db
from backend.core.scheduler import start_scheduler
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Face Attendance & Payroll System")

# Routers
app.include_router(employee.router)
app.include_router(attendance.router)
app.include_router(payroll.router)
app.include_router(leave.router)

# CORS (allow frontend access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()
    start_scheduler()
