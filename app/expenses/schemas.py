from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from typing import Literal
from typing import List


class IncomeSchema(BaseModel):
    amount: int

    class Config:
        from_attributes = True


class SavingSchema(BaseModel):
    amount: int

    class Config:
        from_attributes = True


class Catagory(str, Enum):
    FOOD = "Food"
    TRANSPORT = "Transport"
    ENTERTAINMENT = "Entertainment"
    UTILITIES = "Utilities"
    HEALTHCARE = "Healthcare"
    EDUCATION = "Education"
    PERSONAL_CARE = "Personal Care"
    MISCELLANEOUS = "Miscellaneous"


class CatagoryShow(BaseModel):
    name: str

    class Config:
        from_attributes = True


class ExpenseSource(str, Enum):
    INCOME = "income"
    SAVINGS = "savings"


class ExpenseCreate(BaseModel):
    amount: int
    source: ExpenseSource
    catagory: Catagory


class ExpenseShow(BaseModel):
    id: int
    amount: int
    created_at: datetime
    catagory: Catagory

    class Config:
        from_attributes = True
        

class PlannedExpense(BaseModel):
    catagory: Catagory
    amount: int

class MonthlyPlanCreate(BaseModel):
    planned_expenses: List[PlannedExpense]
