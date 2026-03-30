try:
    import pysqlite3
    import sys
    sys.modules["sqlite3"] = pysqlite3
except ImportError:
    pass

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# Updated for Vercel/Production resilience
if os.getenv("VERCEL"):
    DATABASE_URL = "sqlite:////tmp/supportai.db"
else:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./supportai.db")

# For SQLite, we need connect_args={"check_same_thread": False}
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=True, future=True)
else:
    engine = create_engine(DATABASE_URL, echo=True, future=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    try:
        print(f"Initializing database at: {DATABASE_URL}")
        import backend.models.user
        import backend.models.policy_document
        import backend.models.ticket
        import backend.models.ai_response
        Base.metadata.create_all(bind=engine)
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
