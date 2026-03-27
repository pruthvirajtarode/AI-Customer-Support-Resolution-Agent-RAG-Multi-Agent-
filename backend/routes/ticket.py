from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import SessionLocal, get_db
from backend.models.ticket import Ticket
from backend.models.ai_response import AIResponse
from backend.routes.auth import get_current_user
from backend.agents.pipeline import process_ticket
import json

router = APIRouter()

@router.post("/submit")
def submit_ticket(ticket_text: str, order_json: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    ticket = Ticket(user_id=user.id, ticket_text=ticket_text, order_json=order_json)
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    # AI pipeline
    ai_result = process_ticket(ticket, user.id)
    ai_response = AIResponse(ticket_id=ticket.id, **ai_result)
    db.add(ai_response)
    db.commit()
    db.refresh(ai_response)
    return ai_result

@router.get("/list")
def list_tickets(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Ticket).filter(Ticket.user_id == user.id).all()

@router.get("/responses")
def get_responses(db: Session = Depends(get_db), user=Depends(get_current_user)):
    tickets = db.query(Ticket).filter(Ticket.user_id == user.id).all()
    responses = db.query(AIResponse).filter(AIResponse.ticket_id.in_([t.id for t in tickets])).all()
    return responses
