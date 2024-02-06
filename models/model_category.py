from typing import Annotated
from fastapi import Depends
from database import Base, SessionLocal
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from slugify import slugify
from sqlalchemy.orm import Session


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    slug = Column(String, unique=True, index=True)
    parent_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    is_active = Column(Boolean, default=True)



    def generate_slug(self, db: db_dependency):
        if self.parent_id is not None:
            parent_category = db.query(Category).filter(Category.id == self.parent_id).first()
            parent_slug = parent_category.slug if parent_category else ''
            self.slug = f'{parent_slug}-{slugify(self.name)}'
        else:
            self.slug = slugify(self.name)

