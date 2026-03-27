from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from backend.database import Base

class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ticket_text = Column(Text, nullable=False)
    order_json = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
