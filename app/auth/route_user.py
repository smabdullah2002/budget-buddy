from fastapi import Depends, APIRouter, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from .schemas import UserCreate, ShowUser
from .services import RegisterUser, LoginUser
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.core.jwt_handler import TokenGenerator
from app.core.getuser import get_user


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


@router.post("/signup", response_model=ShowUser, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db=Depends(get_db)):
    new_user = await RegisterUser.create_new_user(user=user, db=db)
    # print("new_user==========>", new_user)
    return new_user


@router.post("/login")
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)
):
    token = await LoginUser.authenticate_user(
        email=form_data.username, password=form_data.password, db=db
    )
    return token


@router.get("/me", response_model=ShowUser)
async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    payload = TokenGenerator.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    user = await get_user(email=payload.get("sub"), db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


# just to check if the token is being received correctly
# @router.get("/me")
# async def read_users_me(token: str = Depends(oauth2_scheme)):
#     payload = TokenGenerator.verify_token(token)
#     if not payload:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid or expired token",
#             # headers={"WWW-Authenticate": "Bearer"},
#         )
#     return {"email": payload.get("sub")}
