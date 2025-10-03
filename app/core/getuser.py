from sqlalchemy import select
from app.auth.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

async def get_user(email: str, db: AsyncSession):
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalars().first()
    return user
