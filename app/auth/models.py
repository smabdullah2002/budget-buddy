from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime
from app.database import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    # connected to expenses
    total_income = Column(Integer, default=0)
    total_savings = Column(Integer, default=0)

    expenses = relationship(
        "Expense", back_populates="owner", cascade="all, delete-orphan"
    )
