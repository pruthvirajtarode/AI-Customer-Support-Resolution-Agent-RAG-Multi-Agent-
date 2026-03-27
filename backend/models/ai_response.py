from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from backend.database import Base

class AIResponse(Base):
    __tablename__ = "ai_responses"
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    classification = Column(String, nullable=False)
    decision = Column(String, nullable=False)
    rationale = Column(Text, nullable=False)
    response_text = Column(Text, nullable=False)
    citations = Column(Text, nullable=False)  # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
