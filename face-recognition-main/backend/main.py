from backend.core.app import app
from backend.core.scheduler import start_scheduler

if __name__ == "__main__":
    start_scheduler()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
