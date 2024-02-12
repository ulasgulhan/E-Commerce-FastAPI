from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from database import SessionLocal
from sqlalchemy.orm import Session
from starlette import status
from models.model_cart import Cart, Cart_Item
from models.model_product import Product
from routers.auth import get_current_user


router = APIRouter(prefix='/cart', tags=['cart'])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get('/', status_code=status.HTTP_200_OK)
async def get_cart(db: db_dependency, user: user_dependency):
    cart_items = db.query(Cart_Item).filter(Cart_Item.user_id == user.get('id'), Cart_Item.is_active == True, Cart_Item.quantity >= 1).all()

    if not cart_items:
        return{
            'Message': 'Your cart is empty'
        }
    
    total = 0
    cart = []

    for item in cart_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        sub_total = product.price * item.quantity
        total += sub_total
        cart.append({
            'Product': product,
            'Quantity': item.quantity,
            'Subtotal': sub_total
        })

    return{
        'Cart': cart,
        'Total': total
    } 
    

@router.patch('/remove', status_code=status.HTTP_200_OK)
async def remove_item(db: db_dependency, user: user_dependency, itm_id: int):
    cart_item = db.query(Cart_Item).filter(Cart_Item.user_id == user.get('id'), Cart_Item.product_id == itm_id, Cart_Item.is_active == True).first()

    if not cart_item:
        return{
            'status_code': status.HTTP_404_NOT_FOUND,
            'detail': 'There is not in the cart'
        }
    
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
    else:
        cart_item.quantity = 0
        cart_item.is_active = False

    db.add(cart_item)
    db.commit()

    return{
        'status_code': status.HTTP_200_OK,
        'detail': 'Item removed'
    }


@router.delete('/delete', status_code=status.HTTP_200_OK)
async def delete_item(db: db_dependency, user: user_dependency, itm_id: int):
    cart_item = db.query(Cart_Item).filter(Cart_Item.user_id == user.get('id'), Cart_Item.product_id == itm_id, Cart_Item.is_active == True).first()
    
    if not cart_item:
        return{
            'status_code': status.HTTP_404_NOT_FOUND,
            'detail': 'There is not in the cart'
        }
    
    cart_item.is_active = False
    cart_item.quantity = 0

    db.add(cart_item)
    db.commit()

    return{
        'status_code': status.HTTP_200_OK,
        'detail': 'Item deleted'
    }



