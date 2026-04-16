from fastapi import APIRouter, UploadFile, Form
from backend.core.database import SessionLocal
from backend.core.crud import create_employee, add_face_encoding
import face_recognition

router = APIRouter(prefix="/employee", tags=["Employee"])

@router.post("/")
async def add_employee(
    emp_id: str = Form(...),
    name: str = Form(...),
    department: str = Form(None),
    position: str = Form(None),
    salary: float = Form(None),
    photo: UploadFile = None
):
    db = SessionLocal()
    photo_bytes = await photo.read()
    emp = create_employee(db, emp_id, name, department, position, salary, photo_bytes)
    image = face_recognition.load_image_file(photo.file)
    boxes = face_recognition.face_locations(image)
    encs = face_recognition.face_encodings(image, boxes)
    for enc in encs:
        add_face_encoding(db, emp_id, enc)
    db.close()
    return {"message": f"Employee {name} added successfully!"}
