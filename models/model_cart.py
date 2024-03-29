from sqlalchemy import DateTime, String, Integer, Boolean, Column, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class Cart(Base):
    __tablename__ = 'carts'

    id = Column(Integer, primary_key=True, index=True)
    date_added = Column(DateTime, default=datetime.now())
    is_active = Column(Boolean, default=True)

    cart_items = relationship('Cart_Item', back_populates='cart')


class Cart_Item(Base):
    __tablename__ = 'cart_items'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer)
    cart_id = Column(Integer, ForeignKey('carts.id'))
    is_active = Column(Boolean, default=True)

    user = relationship('User', back_populates='cart_items')
    products = relationship('Product', back_populates='cart_items')
    cart = relationship('Cart', back_populates='cart_items')

