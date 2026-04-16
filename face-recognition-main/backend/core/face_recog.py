import pickle
from backend.core.database import SessionLocal
from backend.core.models import FaceEncoding

def load_known_faces():
    db = SessionLocal()
    rows = db.query(FaceEncoding).all()
    encs, meta = [], []
    for row in rows:
        encs.append(pickle.loads(row.encoding))
        meta.append(row.employee_id)
    db.close()
    return encs, meta
