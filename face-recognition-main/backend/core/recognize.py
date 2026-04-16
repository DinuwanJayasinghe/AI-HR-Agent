import cv2, numpy as np, face_recognition
from backend.core.face_recog import load_known_faces
from backend.core.database import SessionLocal
from backend.core.crud import mark_attendance
from backend.core.utils import image_to_bytes
from backend.core.config import MODEL, TOLERANCE

def start_camera():
    db = SessionLocal()
    known_encs, known_ids = load_known_faces()
    print(f"Loaded {len(known_encs)} known faces")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Cannot open camera")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb, model=MODEL)
        encs = face_recognition.face_encodings(rgb, boxes)

        for (top, right, bottom, left), enc in zip(boxes, encs):
            if len(known_encs) == 0: continue
            dists = face_recognition.face_distance(known_encs, enc)
            idx = np.argmin(dists)
            if dists[idx] < TOLERANCE:
                emp_id = known_ids[idx]
                mark_attendance(db, emp_id, image_to_bytes(frame))
                color, label = (0,255,0), f"ID: {emp_id}"
            else:
                color, label = (0,0,255), "Unknown"

            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, label, (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        cv2.imshow("Attendance Camera", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    db.close()
