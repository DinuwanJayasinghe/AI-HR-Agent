import cv2
import base64
import datetime as dt
from backend.core.config import TIMEZONE

def now():
    return dt.datetime.now(TIMEZONE)

def image_to_bytes(frame):
    _, buffer = cv2.imencode(".jpg", frame)
    return buffer.tobytes()

def bytes_to_base64(b):
    return base64.b64encode(b).decode("utf-8")

def base64_to_bytes(data: str):
    return base64.b64decode(data)
