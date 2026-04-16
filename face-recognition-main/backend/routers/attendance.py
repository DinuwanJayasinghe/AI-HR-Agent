from fastapi import APIRouter, UploadFile, File
from backend.core.database import SessionLocal
from backend.core.models import AttendanceLog, Employee
from backend.core.face_recog import load_known_faces
from backend.core.crud import mark_attendance
from backend.core.utils import image_to_bytes, bytes_to_base64
from backend.core.config import MODEL, TOLERANCE
import face_recognition
import cv2
import numpy as np

router = APIRouter(prefix="/attendance", tags=["Attendance"])

@router.get("/today")
def today_logs():
    db = SessionLocal()
    logs = db.query(AttendanceLog).all()
    res = [{
        "employee_id": log.employee_id,
        "date": str(log.date),
        "check_in": str(log.check_in),
        "check_out": str(log.check_out),
        "work_hours": log.work_hours,
        "overtime_hours": log.overtime_hours
    } for log in logs]
    db.close()
    return res

@router.post("/recognize")
async def recognize_and_mark(
    image: UploadFile = File(...),
    latitude: float = None,
    longitude: float = None
):
    """
    Recognize face from uploaded image and mark attendance with GPS location
    """
    db = SessionLocal()

    # Load known faces from database
    known_encs, known_ids = load_known_faces()

    if len(known_encs) == 0:
        db.close()
        return {"error": "No employees registered in the system"}

    # Read uploaded image
    contents = await image.read()
    nparr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if frame is None:
        db.close()
        return {"error": "Invalid image"}

    # Convert to RGB for face_recognition
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect faces and get encodings
    boxes = face_recognition.face_locations(rgb, model=MODEL)
    encs = face_recognition.face_encodings(rgb, boxes)

    if len(boxes) == 0:
        db.close()
        return {"error": "No face detected in image"}

    results = []

    for (top, right, bottom, left), enc in zip(boxes, encs):
        # Compare with known faces
        dists = face_recognition.face_distance(known_encs, enc)
        idx = np.argmin(dists)

        if dists[idx] < TOLERANCE:
            emp_id = known_ids[idx]

            # Get employee details
            employee = db.query(Employee).filter(Employee.id == emp_id).first()

            # Mark attendance with GPS location
            log = mark_attendance(db, emp_id, image_to_bytes(frame), latitude, longitude)

            # Determine if this was check-in or check-out
            if log.check_out is None:
                action = "CHECK-IN"
                status_msg = f"✓ {employee.name} - Checked In at {log.check_in.strftime('%H:%M:%S')}"
            else:
                action = "CHECK-OUT"
                status_msg = f"✓ {employee.name} - Checked Out at {log.check_out.strftime('%H:%M:%S')}"
                status_msg += f"\nWork Hours: {log.work_hours} hrs"
                if log.overtime_hours > 0:
                    status_msg += f" (Overtime: {log.overtime_hours} hrs)"

            # Draw rectangle on frame
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, f"{employee.name} - {action}", (left, top-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            results.append({
                "recognized": True,
                "employee_id": emp_id,
                "employee_name": employee.name,
                "department": employee.department,
                "position": employee.position,
                "action": action,
                "check_in": str(log.check_in) if log.check_in else None,
                "check_out": str(log.check_out) if log.check_out else None,
                "check_in_latitude": log.check_in_latitude,
                "check_in_longitude": log.check_in_longitude,
                "check_out_latitude": log.check_out_latitude,
                "check_out_longitude": log.check_out_longitude,
                "work_hours": log.work_hours,
                "overtime_hours": log.overtime_hours,
                "message": status_msg,
                "confidence": float(1 - dists[idx])
            })
        else:
            # Unknown face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.putText(frame, "Unknown", (left, top-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            results.append({
                "recognized": False,
                "message": "Face not recognized",
                "confidence": float(1 - dists[idx])
            })

    # Encode processed frame to base64 for returning to client
    _, buffer = cv2.imencode('.jpg', frame)
    processed_image = bytes_to_base64(buffer.tobytes())

    db.close()

    return {
        "results": results,
        "processed_image": processed_image,
        "faces_detected": len(boxes)
    }

@router.get("/employee/{emp_id}")
def get_employee_attendance(emp_id: str):
    """
    Get attendance records for a specific employee
    """
    db = SessionLocal()
    logs = db.query(AttendanceLog).filter(AttendanceLog.employee_id == emp_id).all()

    res = [{
        "date": str(log.date),
        "check_in": str(log.check_in),
        "check_out": str(log.check_out),
        "work_hours": log.work_hours,
        "overtime_hours": log.overtime_hours
    } for log in logs]

    db.close()
    return res
