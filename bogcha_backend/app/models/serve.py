from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.database import Base

class Serve(Base):
    __tablename__ = "meal_serve_logs"
    id = Column(Integer, primary_key=True, index=True)
    meal_name = Column(String, nullable=False)
    served_by = Column(String, nullable=False)
    served_at = Column(DateTime, default=datetime.utcnow)
