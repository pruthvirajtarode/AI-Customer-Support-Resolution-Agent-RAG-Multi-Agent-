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
    if not file.filename.lower().endswith((".txt", ".pdf")):
        raise HTTPException(status_code=400, detail="Only .txt and .pdf files are supported.")
    
    try:
        content = file.file.read()
        if file.filename.lower().endswith(".pdf"):
            from PyPDF2 import PdfReader
            import io
            try:
                reader = PdfReader(io.BytesIO(content))
                text = ""
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                if not text.strip():
                    raise ValueError("Could not extract text from PDF (it might be scanned or empty)")
            except Exception as e:
                raise HTTPException(status_code=422, detail=f"PDF Parsing Error: {str(e)}")
        else:
            text = content.decode("utf-8", errors="ignore")
            
        if not text.strip():
            raise HTTPException(status_code=400, detail="The uploaded file is empty or contains no readable text.")

        # Store in DB
        doc = PolicyDocument(user_id=user.id, filename=file.filename, content=text)
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        # Process for RAG
        chunks_count = process_policy_document(doc, user.id)
        return {"msg": "Knowledge base synchronized successfully", "indexed_chunks": chunks_count}
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
