from ast import For
from typing import Annotated
from fastapi import Depends
from slugify import slugify
from database import Base
from sqlalchemy import Float, String, Integer, Boolean, Column, ForeignKey
from sqlalchemy.orm import relationship, Session
from database import Base, SessionLocal
from .model_category import Category
from datetime import datetime



def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    slug = Column(String, unique=True, index=True)
    description = Column(String)
    price = Column(Integer)
    image_url = Column(String)
    stock = Column(Integer)
    supplier_id = Column(Integer, ForeignKey('users.id'))
    category_id = Column(Integer, ForeignKey('categories.id'))
    rating = Column(Float)
    is_active = Column(Boolean, default=True)

    category = relationship('Category', back_populates='products')
    user = relationship('User', back_populates='products')
    comments = relationship('Comment', back_populates='products')
    ratings = relationship('Rating', back_populates='products')
    cart_item = relationship('Cart_Item', back_populates='products')


    def generate_slug(self):
        self.slug = slugify(self.name)


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    comment = Column(String)
    parent_id = Column(Integer, ForeignKey('comments.id'), nullable=True)
    is_active = Column(Boolean, default=True)
    post_date = Column(String, default=datetime.utcnow())
    rating = Column(Integer, nullable=True)

    user = relationship('User', back_populates='comments')
    products = relationship('Product', back_populates='comments')
    ratings = relationship('Rating', back_populates='comments')



class Rating(Base):
    __tablename__ = 'ratings'

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    comment_id = Column(Integer, ForeignKey('comments.id'))
    rating = Column(Integer)
    is_active = Column(Boolean, default=True)

    user = relationship('User', back_populates='ratings')
    products = relationship('Product', back_populates='ratings')
    comments = relationship('Comment', back_populates='ratings')
    



