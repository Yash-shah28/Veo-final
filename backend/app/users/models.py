from pydantic import BaseModel, Field, EmailStr, BeforeValidator
from typing import Optional, Annotated
from bson import ObjectId

# Helper to map ObjectId to str
PyObjectId = Annotated[str, BeforeValidator(lambda x: str(x) if x is not None else None)]

class UserBase(BaseModel):
    email: EmailStr
    username: str
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    hashed_password: str

class User(UserBase):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
