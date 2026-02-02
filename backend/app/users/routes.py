from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.database import db
from app.users.models import User, UserCreate

router = APIRouter()

from app.auth.utils import get_password_hash
from fastapi import status

@router.post("/", response_model=User)
async def create_user(user: UserCreate):
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    user_dict = user.model_dump()
    user_dict["hashed_password"] = get_password_hash(user_dict.pop("password"))
    
    new_user = await db.users.insert_one(user_dict)
    created_user = await db.users.find_one({"_id": new_user.inserted_id})
    return User(**created_user)

@router.get("/", response_model=List[User])
async def read_users():
    users = await db.users.find().to_list(1000)
    return [User(**user) for user in users]
