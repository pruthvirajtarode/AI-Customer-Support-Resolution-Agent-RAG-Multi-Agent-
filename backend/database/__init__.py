from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# Updated for Vercel/Production resilience
if os.getenv("VERCEL"):
    DATABASE_URL = "sqlite:////tmp/supportai.db"
    # Ensure /tmp exists
    try:
        os.makedirs("/tmp", exist_ok=True)
    except Exception:
        pass
else:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./supportai.db")

print(f"DEBUG: Using DATABASE_URL={DATABASE_URL}")

# For SQLite, we need connect_args={"check_same_thread": False}
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=True, future=True)
else:
    engine = create_engine(DATABASE_URL, echo=True, future=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    try:
        print(f"DEBUG: Initializing database at {DATABASE_URL}")
        import backend.models.user
        import backend.models.policy_document
        import backend.models.ticket
        import backend.models.ai_response
        Base.metadata.create_all(bind=engine)
        print("DEBUG: Database tables created successfully.")
    except Exception as e:
        import traceback
        error_msg = f"CRITICAL: Database initialization failed: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        if os.getenv("VERCEL"):
            raise RuntimeError(error_msg)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
