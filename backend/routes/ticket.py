from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import SessionLocal, get_db
from backend.models.ticket import Ticket
from backend.models.ai_response import AIResponse
from backend.routes.auth import get_current_user
from backend.agents.pipeline import process_ticket
import json

router = APIRouter()

from pydantic import BaseModel

class TicketRequest(BaseModel):
    text: str
    order_json: dict = {}

@router.post("/audit")
def audit_ticket(data: TicketRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    try:
        ticket = Ticket(user_id=user.id, ticket_text=data.text, order_json=json.dumps(data.order_json))
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        
        # AI pipeline
        ai_result = process_ticket(ticket, user.id, db=db)
        
        # Map agent results to AIResponse model
        ai_response = AIResponse(
            ticket_id=ticket.id,
            classification=ai_result.get("classification", "other"),
            decision=ai_result.get("decision", "escalate"),
            rationale=ai_result.get("rationale", ""),
            response_text=ai_result.get("customer_response", ""),
            citations=json.dumps(ai_result.get("citations", []))
        )
        db.add(ai_response)
        db.commit()
        return ai_result
    except Exception as e:
        import traceback
        print(f"ERROR: Ticket Audit Failed: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
def list_tickets(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Ticket).filter(Ticket.user_id == user.id).all()

@router.get("/history")
def get_ticket_history(db: Session = Depends(get_db), user=Depends(get_current_user)):
    # Join Ticket and AIResponse for the dashboard
    results = db.query(Ticket, AIResponse).join(AIResponse, Ticket.id == AIResponse.ticket_id).filter(Ticket.user_id == user.id).order_by(Ticket.id.desc()).all()
    
    history = []
    for t, r in results:
        history.append({
            "id": t.id,
            "ticket_text": t.ticket_text,
            "category": r.classification,
            "decision": r.decision,
            "response_text": r.response_text
        })
    return history

@router.get("/responses")
def get_responses(db: Session = Depends(get_db), user=Depends(get_current_user)):
    tickets = db.query(Ticket).filter(Ticket.user_id == user.id).all()
    responses = db.query(AIResponse).filter(AIResponse.ticket_id.in_([t.id for t in tickets])).all()
    return responses

@router.get("/stats")
def get_ticket_stats(db: Session = Depends(get_db), user=Depends(get_current_user)):
    total = db.query(Ticket).filter(Ticket.user_id == user.id).count()
    responses = db.query(AIResponse).join(Ticket).filter(Ticket.user_id == user.id).all()
    
    approvals = sum(1 for r in responses if r.decision.lower() == "approve")
    denials = sum(1 for r in responses if r.decision.lower() == "deny")
    escalations = sum(1 for r in responses if r.decision.lower() == "escalate")
    
    compliance = (approvals + denials) / len(responses) if responses else 0
    
    # Activity Stats (Last 7 days)
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    activity = []
    for i in range(6, -1, -1):
        day = (datetime.utcnow() - timedelta(days=i)).date()
        count = db.query(Ticket).filter(
            Ticket.user_id == user.id,
            func.date(Ticket.created_at) == day
        ).count()
        activity.append({"day": day.strftime("%a"), "count": count})
    
    return {
        "total_audits": total,
        "compliance_rate": f"{compliance * 100:.1f}%",
        "avg_latency": "840ms",
        "activity": activity,
        "status_summary": {
            "approvals": approvals,
            "denials": denials,
            "escalations": escalations
        }
    }
