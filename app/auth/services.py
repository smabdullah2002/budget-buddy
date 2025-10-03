from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import UserCreate, ShowUser
from .models import User
from app.core.hashing import Hasher
from app.core.jwt_handler import TokenGenerator
from app.core.getuser import get_user
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")


class RegisterUser:
    @staticmethod
    async def create_new_user(user: UserCreate, db: AsyncSession):
        user_in_db = await get_user(email=user.email, db=db)
        if user_in_db:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        new_user = User(
            email=user.email,
            username=user.username,
            password=Hasher.hash_password(user.password),
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return new_user


class LoginUser:
    @staticmethod
    async def authenticate_user(email: str, password: str, db: AsyncSession):
        user = await get_user(email=email, db=db)
        if not user or not Hasher.verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect email or password",
            )
        access_token = TokenGenerator.create_token(
            data={"sub": user.email},
            expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )

        return {"access_token": access_token, "token_type": "bearer"}



