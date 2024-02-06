from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated, Optional
from sqlalchemy.orm import Session
from starlette import status
from pydantic import BaseModel
from database import SessionLocal
from models.model_category import Category
from .auth import get_current_user


router = APIRouter(prefix='/category', tags=['category'])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class CreateCategory(BaseModel):
    name: str
    parent_id: Optional[int] = None



@router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_category(db: db_dependency, user: user_dependency, create_category: CreateCategory):
    try:
        if user.get('role') == 'admin':
            category_model = Category(
                name = create_category.name,
                parent_id = create_category.parent_id,
            )

            category_model.generate_slug(db)

            db.add(category_model)
            db.commit()

            return{
                'status_code': 201,
                'transaction': 'Successful'
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='You must be admin user for this'
            )
    except Exception as err:
        return{
            'error': str(err)
        }

