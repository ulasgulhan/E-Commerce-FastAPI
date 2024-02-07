import stat
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from database import SessionLocal
from sqlalchemy.orm import Session
from starlette import status
from .auth import get_current_user
from models.model_user import User


router = APIRouter(prefix='/permission', tags=['permission'])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
         db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.patch('/', status_code=status.HTTP_200_OK)
async def user_permission(db: db_dependency, get_user: user_dependency, user_id: int):
    if get_user.get('is_admin'):
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found'
            )
        
        if user.is_supplier:
            user.is_supplier = False
            db.add(user)
            db.commit()
            return{
                'status_code': status.HTTP_200_OK,
                'detail': 'User is no longer supplier'
            }
        else:
            user.is_supplier = True
            db.add(user)
            db.commit()
            return{
                'status_code': status.HTTP_200_OK,
                'detail': 'User is now supplier'
            }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You don't have admin permission"
        )


@router.delete('/delete', status_code=status.HTTP_200_OK)
async def delete_user(db: db_dependency, get_user: user_dependency, user_id: int):
    if get_user.get('is_admin'):
        user = db.query(User).filter(User.id == user_id).first()

        if user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You can't delete admin user"
            )
        
        if user.is_active:
            user.is_active = False
            db.add(user)
            db.commit()
            return{
                'status_code': status.HTTP_200_OK,
                'detail': 'User is deleted'
            }
        else:
            user.is_active = True
            db.add(user)
            db.commit()
            return{
                'status_code': status.HTTP_200_OK,
                'detail': 'User is activated'
            }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You don't have admin permission"
        )



