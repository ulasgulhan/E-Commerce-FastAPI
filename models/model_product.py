from ast import For
from typing import Annotated
from fastapi import Depends
from slugify import slugify
from database import Base
from sqlalchemy import String, Integer, Boolean, Column, ForeignKey
from sqlalchemy.orm import relationship, Session
from database import Base, SessionLocal
from .model_category import Category



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
    supplier_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    category_id = Column(Integer, ForeignKey('categories.id'))
    is_active = Column(Boolean, default=True)

    category = relationship('Category', back_populates='products')
    user = relationship('User', back_populates='products')


    def generate_slug(self):
        self.slug = slugify(self.name)



