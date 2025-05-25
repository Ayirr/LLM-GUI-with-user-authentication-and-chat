from fastapi import APIRouter, HTTPException, status, Depends
from app.models import UserCreate, UserLogin, Token, User
from app.auth import get_password_hash, verify_password, create_access_token, get_current_user
from app.database import users_collection
from datetime import datetime, timedelta
from decouple import config

router = APIRouter()

@router.post("/register", response_model=dict)
async def register(user: UserCreate):
    # Check if user already exists
    existing_user = await users_collection.find_one({"$or": [{"username": user.username}, {"email": user.email}]})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    user_doc = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    result = await users_collection.insert_one(user_doc)
    return {"message": "User created successfully", "user_id": str(result.inserted_id)}

@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    db_user = await users_collection.find_one({"username": user.username})
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=int(config("ACCESS_TOKEN_EXPIRE_MINUTES")))
    access_token = create_access_token(
        data={"sub": db_user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=dict)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return {
        "id": str(current_user["_id"]),
        "username": current_user["username"],
        "email": current_user["email"],
        "created_at": current_user["created_at"],
        "is_active": current_user["is_active"]
    }