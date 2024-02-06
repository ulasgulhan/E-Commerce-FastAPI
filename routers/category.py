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
                'status_code': status.HTTP_201_CREATED,
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


@router.get('/all_categories', status_code=status.HTTP_200_OK)
async def get_all_categories(db: db_dependency):
    categories = db.query(Category).filter(Category.is_active == True).all()

    if categories is not None:
        return categories
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail='There is no category found'
    )


@router.put('/update_category', status_code=status.HTTP_200_OK)
async def update_category(db: db_dependency, user: user_dependency, category_id: int, update_category: CreateCategory):
    category = db.query(Category).filter(Category.id == category_id).first()
    category_parent = category.parent_id
    category_name = category.name

    if user.get('role') == 'admin':
        if category is not None:
            category.name = update_category.name
            category.parent_id = update_category.parent_id

            if update_category.parent_id is None:
                category.parent_id = category_parent
            
            if update_category.name is None:
                category.name = category_name

            db.add(category)
            db.commit()

            return{
                'status_code': status.HTTP_200_OK,
                'transaction': 'Category update is successful'
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There is no category found'
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You must be admin user for this'
        )


@router.delete('/delete', status_code=status.HTTP_200_OK)
async def delete_category(db: db_dependency, user: user_dependency, category_id: int):
    category = db.query(Category).filter(Category.id == category_id).first()

    if user.get('role') == 'admin':
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There is no category found'
            )
        
        category.is_active = False
        db.add(category)
        db.commit()

        return{
            'status_code': status.HTTP_200_OK,
            'transaction': 'Category update is successful'
        }
        
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You must be admin user for this'
        )

