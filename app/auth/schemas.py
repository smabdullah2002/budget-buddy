from pydantic import BaseModel,EmailStr,Field

class UserCreate(BaseModel):
    email:EmailStr
    username:str
    password:str=Field(min_length=4)
    
    class Config:
        from_attributes =True


class ShowUser(BaseModel):
    id:int
    email:EmailStr
    username:str
    total_income:int
    total_savings:int
    
    class Config:
        from_attributes =True
    