from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime

from . import schemas
from app.database import Base


class Expense(Base):
    __tablename__ = "expenses_table"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    catagory = Column(Enum(schemas.Catagory), nullable=False)

    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    owner = relationship("User", back_populates="expenses")
    
class BudgetPlan(Base):
    __tablename__="budget_plans"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    year=Column(Integer, nullable=False)
    month=Column(Integer, nullable=False)
    category=Column(Enum(schemas.Catagory), nullable=False)
    planned_amount=Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
