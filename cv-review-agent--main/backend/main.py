from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.api import router  # Import the router from routes

import logging

app = FastAPI(title="CV Review & Analysis API", version="1.0.0")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include modular routes
app.include_router(router, prefix="/api")

# Health check
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "CV Review API is healthy."}

# Startup event
@app.on_event("startup")
async def on_startup():
    logging.info("🚀 FastAPI is starting up...")

# Shutdown event
@app.on_event("shutdown")
async def on_shutdown():
    logging.info("🛑 FastAPI is shutting down...")

# Run with: python main.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
