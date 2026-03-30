from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import SessionLocal, get_db
from backend.models.policy_document import PolicyDocument
from backend.routes.auth import get_current_user
from backend.rag.pipeline import process_policy_document
import os

router = APIRouter()

@router.post("/sync")
def upload_policy(file: UploadFile = File(...), db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not file.filename.endswith((".txt", ".pdf")):
        raise HTTPException(status_code=400, detail="Only txt/pdf allowed")
    content = file.file.read()
    if file.filename.endswith(".pdf"):
        from PyPDF2 import PdfReader
        import io
        reader = PdfReader(io.BytesIO(content))
        text = "\n".join([page.extract_text() or "" for page in reader.pages])
    else:
        text = content.decode("utf-8")
    # Store in DB
    doc = PolicyDocument(user_id=user.id, filename=file.filename, content=text)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    # Process for RAG
    chunks_count = process_policy_document(doc, user.id)
    return {"msg": "Uploaded and processed", "indexed_chunks": chunks_count}
