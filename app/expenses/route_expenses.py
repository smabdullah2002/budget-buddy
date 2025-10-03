from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from .services import ExpenseManagement, ExpensePlanner
from .schemas import (
    IncomeSchema,
    SavingSchema,
    ExpenseCreate,
    ExpenseShow,
    CatagoryShow,
    MonthlyPlanCreate,
)
from app.auth.route_user import get_current_user
from app.auth.schemas import ShowUser


router = APIRouter()


@router.put("/income/", status_code=status.HTTP_201_CREATED, response_model=ShowUser)
async def add_income(
    income_data: IncomeSchema,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    print("current_user===========>", current_user)
    updated_income = await ExpenseManagement.update_income(
        income_data=income_data, db=db, current_user=current_user
    )
    return updated_income


@router.put("/savings/", status_code=status.HTTP_201_CREATED, response_model=ShowUser)
async def add_savings(
    saving_data: SavingSchema,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    updated_savings = await ExpenseManagement.update_savings(
        saving_data=saving_data, db=db, current_user=current_user
    )
    return updated_savings


@router.post(
    "/expense/", status_code=status.HTTP_201_CREATED, response_model=ExpenseShow
)
async def add_expense(
    expense_data: ExpenseCreate,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    new_expense = await ExpenseManagement.add_expense(
        expense_data=expense_data, db=db, current_user=current_user
    )
    return new_expense


@router.get(
    "/expense/", status_code=status.HTTP_200_OK, response_model=list[ExpenseShow]
)
async def get_expense_list(
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    expenses = await ExpenseManagement.expense_list(db=db, current_user=current_user)
    return expenses


@router.get(
    "/expense/{catagory}",
    status_code=status.HTTP_200_OK,
    response_model=list[ExpenseShow],
)
async def get_expense_by_catagory(
    catagory: str,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    expenses = await ExpenseManagement.expense_list_by_catagory(
        catagory=catagory, db=db, current_user=current_user
    )
    return expenses


@router.delete("/expense/{id}", status_code=status.HTTP_200_OK, response_model=ShowUser)
async def delete_expense(
    id: int,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    updated_user = await ExpenseManagement.delete_expense(
        id=id, db=db, current_user=current_user
    )
    return updated_user


@router.get("/expense/monthly/{year}/{month}", status_code=status.HTTP_200_OK)
async def get_monthly_report(
    year: int, month: int, db=Depends(get_db), current_user=Depends(get_current_user)
):
    report = await ExpenseManagement.monthly_report(
        year=year, month=month, db=db, current_user=current_user
    )
    return report


@router.post("/budget-plan/{year}/{month}", status_code=status.HTTP_201_CREATED)
async def create_budget_plan(
    year: int,
    month: int,
    plan_data: MonthlyPlanCreate,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await ExpensePlanner.create_budget_plan(
        year=year, month=month, plan_data=plan_data, db=db, current_user=current_user
    )
    return result


@router.get("/budget-plan/{year}/{month}", status_code=status.HTTP_200_OK)
async def get_budget_plan(
    year: int,
    month: int,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await ExpensePlanner.get_budget_plan(
        year=year, month=month, db=db, current_user=current_user
    )
    return result

@router.delete("/budget-plan/{year}/{month}", status_code=status.HTTP_200_OK)
async def delete_budget_plan(
    year: int,
    month: int,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await ExpensePlanner.delete_budget_plan(
        year=year, month=month, db=db, current_user=current_user
    )
    return result


@router.put("/budget-plan/{id}", status_code=status.HTTP_200_OK)
async def update_budget_plan(
    id: int,
    amount: int,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await ExpensePlanner.update_budget_plan(
        id=id, amount=amount, db=db, current_user=current_user
    )
    return result

@router.get("/budget-vs-actual/{year}/{month}", status_code=status.HTTP_200_OK)
async def get_budget_vs_actual(
    year: int,
    month: int,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await ExpensePlanner.budget_vs_actual(
        year=year, month=month, db=db, current_user=current_user
    )
    return result