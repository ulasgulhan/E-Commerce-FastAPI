from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from database import SessionLocal
from sqlalchemy.orm import Session
from models.model_category import Category
from .auth import get_current_user
from starlette import status
from models.model_product import Product


router = APIRouter(prefix='/products', tags=['products'])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class CreateProduct(BaseModel):
    name: str
    description: str
    price: int
    image_url: str
    stock: int
    category: int


@router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_product(db: db_dependency, user: user_dependency, create_model: CreateProduct):
    try:
        if user.get('role') == 'customer':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='You are not authorized for this method'
            )
        else:
            product = Product(
                name = create_model.name,
                description = create_model.description,
                price = create_model.price,
                image_url = create_model.image_url,
                stock = create_model.stock,
                category_id = create_model.category
            )

            product.generate_slug()

            db.add(product)
            db.commit()

            return{
                'status_code': status.HTTP_201_CREATED,
                'transaction': 'Successful'
            }
        
    except Exception as err:
        return{
            'error': str(err)
        }


@router.get('/{category_slug}', status_code=status.HTTP_200_OK)
async def product_by_category(db: db_dependency, category_slug: str):
    category = db.query(Category).filter(Category.slug == category_slug).first()

    if not category:  
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Category not found'
        )
    
    products = []
    categories_to_process = [category]

    while categories_to_process:
        current_category = categories_to_process.pop()

        # products.extend(current_category.products)
        products.extend(db.query(Product).filter(Product.category_id == current_category.id, Product.is_active == True, Product.stock > 0))

        subcategories = db.query(Category).filter(Category.parent_id == current_category.id).all()

        categories_to_process.extend(subcategories)

    return products


@router.get('/detail/{product_slug}', status_code=status.HTTP_200_OK)
async def product_detail(db: db_dependency, product_slug: str):
    product = db.query(Product).filter(Product.slug == product_slug, Product.is_active == True, Product.stock > 0).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product not found'
        )
    
    return product


@router.delete('/delete', status_code=status.HTTP_200_OK)
async def delete_product(db: db_dependency, user: user_dependency, product_id: int):
    if user is not None:
        product = db.query(Product).filter(Product.id == product_id, Product.is_active == True).first()

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Product not found'
            )
        
        product.is_active = False

        db.add(product)
        db.commit()

        return{
            'status_code': status.HTTP_200_OK,
            'detail': 'Product has been deleted'
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You have not permisson to delete product'
        )


