from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from database import SessionLocal
from sqlalchemy.orm import Session
from models.model_category import Category
from .auth import get_current_user
from starlette import status
from models.model_product import Product, Comment, Rating
from models.model_user import User


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


class CreateComment(BaseModel):
    comment: str
    parent_id: Optional[int] = None


class CreateRating(BaseModel):
    rating: int = Field(ge=1, le=5, description='The rating must be between 1 and 5')


@router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_product(db: db_dependency, user: user_dependency, create_model: CreateProduct):
    try:
        if user.get('is_admin') or user.get('is_supplier'):
            product = Product(
            name = create_model.name,
            description = create_model.description,
            price = create_model.price,
            image_url = create_model.image_url,
            stock = create_model.stock,
            category_id = create_model.category
            )

            product.generate_slug()
            product.supplier_id = user.get('id')

            db.add(product)
            db.commit()

            return{
                'status_code': status.HTTP_201_CREATED,
                'transaction': 'Successful'
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='You are not authorized for this method'
            )
        
    except Exception as err:
        return{
            'error': str(err)
        }


@router.get('/', status_code=status.HTTP_200_OK)
async def all_products(db: db_dependency):
    products = db.query(Product).filter(Product.is_active == True, Product.stock > 0).all()
    
    if not products:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no product'
        )
    
    return products


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

        products.extend(db.query(Product).filter(Product.category_id == current_category.id, Product.is_active == True, Product.stock > 0))

        subcategories = db.query(Category).filter(Category.parent_id == current_category.id).all()

        categories_to_process.extend(subcategories)

    return products


@router.get('/detail/{product_slug}', status_code=status.HTTP_200_OK)
async def product_detail(db: db_dependency, product_slug: str):
    product = db.query(Product).filter(Product.slug == product_slug, Product.is_active == True, Product.stock > 0).first()
    comments = db.query(Comment).filter(Comment.product_id == product.id, Comment.is_active == True).order_by('post_date').all()
    

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product not found'
        )
    
    return {
        'Product': product,
        'Comments': comments
    }


@router.post('/detail/{product_slug}/comment', status_code=status.HTTP_201_CREATED)
async def create_comment(db: db_dependency, user: user_dependency, product_slug: str, create_comment: CreateComment, create_rating: CreateRating):
    product = db.query(Product).filter(Product.slug == product_slug, Product.is_active == True, Product.stock > 0).first()
    try:
        comment = Comment(
            comment = create_comment.comment,
            parent_id = create_comment.parent_id
        )
        comment.product_id = product.id
        comment.user_id = user.get('id')

        the_comment = db.query(Comment).filter(Comment.user_id == comment.user_id, Comment.product_id == comment.product_id, Comment.parent_id == None, Comment.is_active == True).first()

        if not the_comment:
            rating = Rating(
                rating = create_rating.rating
            )

            rating.product_id = product.id
            rating.user_id = user.get('id')

            comment.rating = rating.rating

            db.add(comment)
            db.commit()

            rating.comment_id = comment.id

            db.add(rating)
            db.commit()

            ratings = db.query(Rating).filter(Rating.product_id == product.id, Rating.is_active == True).all()
            result = 0
            for rating in ratings:
                result += rating.rating

            result = result/len(ratings)

            product.rating = result

            db.add(product)
            db.commit()

            return{
                'status_code': status.HTTP_201_CREATED,
                'transaction': 'Successful'
            }

        else:
            if comment.parent_id is not None:
                db.add(comment)
                db.commit()

                return{
                    'status_code': status.HTTP_201_CREATED,
                    'transaction': 'Successful'
                }
            else:
                return{
                    'detail': 'You cannot comment two times. You can answere another comment'
                }
    except Exception as err:
        return{
            'error': str(err)
        }


@router.patch('/detail/{product_slug}/comment', status_code=status.HTTP_200_OK)
async def update_comment(db: db_dependency, user: user_dependency, comment_id: int, update_comment: CreateComment):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if comment:
        if user.get('id') == comment.user_id or user.get('is_admin'):
            comment.comment = update_comment.comment
            db.add(comment)
            db.commit()

            return{
                'status_code': status.HTTP_200_OK,
                'detail': 'You successfully delete this comment'
            }



@router.delete('/comment/delete', status_code=status.HTTP_200_OK)
async def delete_comment(db: db_dependency, user: user_dependency, comment_id: int):
    comment = db.query(Comment).filter(Comment.id == comment_id, Comment.is_active == True).first()
    if comment:
        if user.get('id') == comment.user_id or user.get('is_admin'):
            comment.is_active = False
            db.add(comment)
            db.commit()

            rating = db.query(Rating).filter(Rating.product_id == comment.product_id, Rating.comment_id == comment.id).first()
            rating.is_active = False
            db.add(rating)
            db.commit()
            product = db.query(Product).filter(Product.id == comment.product_id).first()

            ratings = db.query(Rating).filter(Rating.product_id == comment.product_id, Rating.is_active == True).all()


            result = 0
            for rate in ratings:
                result += rate.rating

            result = result/len(ratings)

            product.rating = result

            db.add(product)
            db.commit()

            return{
                'status_code': status.HTTP_200_OK,
                'detail': 'You successfully delete this comment'
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='You have not permisson to delete product'
            )
    else:
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail='Comment not found'
        )




@router.get('/supplier/{user_id}', status_code=status.HTTP_200_OK)
async def product_by_supplier(db: db_dependency, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Supplier not found'
        )

    products = db.query(Product).filter(Product.supplier_id == user_id, Product.is_active == True, Product.stock > 0).all()

    if not products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product not found'
        )
    
    return products
    


@router.delete('/delete', status_code=status.HTTP_200_OK)
async def delete_product(db: db_dependency, user: user_dependency, product_id: int):
    product = db.query(Product).filter(Product.id == product_id, Product.is_active == True).first()
    if user.get('id') == product.supplier_id or user.get('is_admin'):

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


