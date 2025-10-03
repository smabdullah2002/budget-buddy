from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import models
from app.database import get_db
from .schemas import IncomeSchema, SavingSchema, ExpenseCreate, MonthlyPlanCreate
from .models import Expense, BudgetPlan
from sqlalchemy.future import select
from sqlalchemy import extract
from collections import defaultdict


class ExpenseManagement:
    @staticmethod
    async def update_income(
        income_data: IncomeSchema, db: AsyncSession, current_user: models.User
    ):
        current_user.total_income += income_data.amount
        db.add(current_user)
        await db.commit()
        await db.refresh(current_user)
        return current_user

    @staticmethod
    async def update_savings(
        saving_data: SavingSchema, db: AsyncSession, current_user: models.User
    ):
        if saving_data.amount > current_user.total_income:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Savings cannot exceed total income",
            )
        current_user.total_savings += saving_data.amount
        current_user.total_income -= saving_data.amount
        db.add(current_user)
        await db.commit()
        await db.refresh(current_user)
        return current_user

    @staticmethod
    async def add_expense(
        expense_data: ExpenseCreate, db: AsyncSession, current_user: models.User
    ):
        if expense_data.source == "income":
            if expense_data.amount > current_user.total_income:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Expense cannot exceed total income",
                )
            else:
                current_user.total_income -= expense_data.amount
        elif expense_data.source == "savings":
            if expense_data.amount > current_user.total_savings:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Expense cannot exceed total savings",
                )
            else:
                current_user.total_savings -= expense_data.amount

        new_expense = Expense(
            amount=expense_data.amount,
            user_id=current_user.id,
            # source=expense_data.source,
            catagory=expense_data.catagory,
        )
        db.add(current_user)
        db.add(new_expense)
        await db.commit()
        await db.refresh(new_expense)
        return new_expense

    @staticmethod
    async def expense_list(db: AsyncSession, current_user: models.User):
        stmt = select(Expense).where(Expense.user_id == current_user.id)
        result = await db.execute(stmt)
        expenses = result.scalars().all()
        return expenses

    @staticmethod
    async def expense_list_by_catagory(
        catagory: str, db: AsyncSession, current_user: models.User
    ):
        stmt = select(Expense).where(
            Expense.user_id == current_user.id, Expense.catagory == catagory
        )
        result = await db.execute(stmt)
        expenses = result.scalars().all()
        return expenses

    @staticmethod
    async def delete_expense(id: int, db: AsyncSession, current_user: models.User):
        stmt = select(Expense).where(
            Expense.id == id, Expense.user_id == current_user.id
        )
        result = await db.execute(stmt)
        expense = result.scalar_one_or_none()
        if not expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found"
            )
        current_user.total_income += expense.amount
        await db.delete(expense)
        await db.commit()
        return {"detail": "Expense deleted successfully"}

    @staticmethod
    async def monthly_report(
        year: int, month: int, db: AsyncSession, current_user: models.User
    ):
        stmt = select(Expense).where(
            Expense.user_id == current_user.id,
            extract("year", Expense.created_at) == year,
            extract("month", Expense.created_at) == month,
        )
        result = await db.execute(stmt)
        expenses = result.scalars().all()

        # total expense calculation
        total_expense = sum(expense.amount for expense in expenses)

        # expense by catagory
        expense_by_catagory = defaultdict(int)
        for expense in expenses:
            expense_by_catagory[expense.catagory] += expense.amount

        percentage_by_catagory = defaultdict(float)
        for catagory, amount in expense_by_catagory.items():
            percentage_by_catagory[catagory] = (
                (amount / total_expense) * 100 if total_expense else 0
            )

        return {
            "year": year,
            "month": month,
            "total_expense": total_expense,
            "expense_by_catagory": expense_by_catagory,
            "percentage_by_catagory": percentage_by_catagory,
        }


class ExpensePlanner:

    @staticmethod
    async def create_budget_plan(
        year: int,
        month: int,
        plan_data: MonthlyPlanCreate,
        db: AsyncSession,
        current_user: models.User,
    ):
        try:
            for item in plan_data.planned_expenses:
                new_plan = BudgetPlan(
                    user_id=current_user.id,
                    year=year,
                    month=month,
                    category=item.catagory,
                    planned_amount=item.amount,
                )
                db.add(new_plan)
            await db.commit()
            return {"detail": "Budget plan created successfully"}
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while creating the budget plan",
            ) from e

    @staticmethod
    async def get_budget_plan(
        year: int, month: int, db: AsyncSession, current_user: models.User
    ):
        stmt = select(BudgetPlan).where(
            BudgetPlan.user_id == current_user.id,
            BudgetPlan.year == year,
            BudgetPlan.month == month,
        )
        result = await db.execute(stmt)
        plans = result.scalars().all()
        return plans

    @staticmethod
    async def update_budget_plan(
        id: int, amount: int, db: AsyncSession, current_user: models.User
    ):
        stmt = select(BudgetPlan).where(
            BudgetPlan.id == id, BudgetPlan.user_id == current_user.id
        )
        result = await db.execute(stmt)
        plan = result.scalar_one_or_none()
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Budget plan not found"
            )
        plan.planned_amount = amount
        await db.commit()
        return {"detail": "Budget plan updated successfully"}

    @staticmethod
    async def delete_budget_plan(
        year: int, month: int, db: AsyncSession, current_user: models.User
    ):
        stmt = select(BudgetPlan).where(
            BudgetPlan.user_id == current_user.id,
            BudgetPlan.year == year,
            BudgetPlan.month == month,
        )
        result = await db.execute(stmt)
        plans = result.scalars().all()
        if not plans:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No budget plan found"
            )
        for plan in plans:
            await db.delete(plan)
        await db.commit()
        return {"detail": "Budget plan deleted successfully"}

    @staticmethod
    async def budget_vs_actual(
        year: int, month: int, db: AsyncSession, current_user: models.User
    ):
        # Fetch budget plans
        stmt = select(BudgetPlan).where(
            BudgetPlan.user_id == current_user.id,
            BudgetPlan.year == year,
            BudgetPlan.month == month,
        )
        result = await db.execute(stmt)
        plans = result.scalars().all()

        # Fetch actual expenses
        stmt = select(Expense).where(
            Expense.user_id == current_user.id,
            extract("year", Expense.created_at) == year,
            extract("month", Expense.created_at) == month,
        )
        result = await db.execute(stmt)
        expenses = result.scalars().all()

        # Calculate actual expenses by category
        actual_by_category = defaultdict(int)
        total_expense = 0
        for expense in expenses:
            actual_by_category[expense.catagory] += expense.amount
            total_expense += expense.amount

        
        # Prepare the comparison data
        comparison = []
        total_planned = sum(plan.planned_amount for plan in plans)
        for plan in plans:
            actual_amount = actual_by_category.get(plan.category, 0)
            comparison.append(
                {
                    "category": plan.category,
                    "planned_amount": plan.planned_amount,
                    "actual_amount": actual_amount,
                }
            )

        return {
            "year": year,
            "month": month,
            "total_planned": total_planned,
            "total_expense": total_expense,
            "comparison": comparison,
        }
