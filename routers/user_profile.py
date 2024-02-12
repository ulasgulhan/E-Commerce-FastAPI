from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session
from database import SessionLocal
from models.model_user import User
from routers.auth import get_current_user
from starlette import status
from passlib.context import CryptContext


router = APIRouter(prefix='/profile', tags=['profile'])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class PasswordVerification(BaseModel):
    password: str
    new_password: str


@router.get('/', status_code=status.HTTP_200_OK)
async def profile(db: db_dependency, get_user: user_dependency):
    user = db.query(User).filter(User.id == get_user.get('id'), User.is_active == True).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found.'
        )
    
    return {
        'Full Name': f'{user.first_name} {user.last_name}',
        'Username': user.username,
        'E-mail': user.email,
        'Products': user.products        
    }


@router.put('/change-password', status_code=status.HTTP_200_OK)
async def change_password(db: db_dependency, get_user: user_dependency, pwd_verification: PasswordVerification):
    if get_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication faild'
        )
    
    user = db.query(User).filter(User.id == get_user.get('id')).first()

    if not bcrypt_context.verify(pwd_verification.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Error on password change'
        )
    
    user.hashed_password = bcrypt_context.hash(pwd_verification.new_password)

    db.add(user)
    db.commit()

    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Successful' 
    }
