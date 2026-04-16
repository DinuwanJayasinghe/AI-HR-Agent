from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.core.models import Base
from backend.core.config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def init_db():
    Base.metadata.create_all(engine)
