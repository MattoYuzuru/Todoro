from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..auth import create_access_token
from ..crud.user_crud import (
    authenticate_user,
    create_user,
    get_current_user,
    get_user_by_id,
    update_user,
    delete_user,
)
from ..db.session import get_db
from ..models import User
from ..schemas.token_schemas import Token
from ..schemas.user_schemas import UserCreate, UserResponse, UserUpdate

router = APIRouter()


@router.post("/login", response_model=Token)
def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token, token_type="bearer")


@router.post("/create", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_new_user(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        return create_user(db, user_data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/users/{user_id}", response_model=UserResponse)
def read_user(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this user")
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/users/", response_model=List[UserResponse])
def read_users(current_user: User = Depends(get_current_user)):
    return [current_user]


@router.get("/users/me/", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/users/{user_id}", response_model=UserResponse)
def update_existing_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this user")
    try:
        user = update_user(db, user_id, user_data)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/users/{user_id}", response_model=UserResponse)
def delete_existing_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this user")
    user = delete_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
