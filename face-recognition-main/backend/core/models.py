from sqlalchemy import Column, String, Integer, LargeBinary, Date, DateTime, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Employee(Base):
    __tablename__ = "employees"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    department = Column(String)
    position = Column(String)
    salary = Column(Float)
    photo = Column(LargeBinary)

    encodings = relationship("FaceEncoding", back_populates="employee")
    attendance = relationship("AttendanceLog", back_populates="employee")
    leaves = relationship("LeaveRecord", back_populates="employee")

class FaceEncoding(Base):
    __tablename__ = "face_encodings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String, ForeignKey("employees.id"))
    encoding = Column(LargeBinary)
    employee = relationship("Employee", back_populates="encodings")

class AttendanceLog(Base):
    __tablename__ = "attendance_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String, ForeignKey("employees.id"))
    date = Column(Date, nullable=False)
    check_in = Column(DateTime)
    check_out = Column(DateTime)
    work_hours = Column(Float)
    overtime_hours = Column(Float)
    snapshot = Column(LargeBinary)
    check_in_latitude = Column(Float)
    check_in_longitude = Column(Float)
    check_out_latitude = Column(Float)
    check_out_longitude = Column(Float)
    employee = relationship("Employee", back_populates="attendance")

class LeaveRecord(Base):
    __tablename__ = "leave_records"
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String, ForeignKey("employees.id"))
    date = Column(Date, nullable=False)
    reason = Column(String)
    type = Column(String)
    approved = Column(Integer, default=0)
    employee = relationship("Employee", back_populates="leaves")
