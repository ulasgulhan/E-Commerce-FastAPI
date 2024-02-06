from fastapi import FastAPI
from database import engine
from models import model_category, model_user
from routers import category, auth


app = FastAPI()

model_user.Base.metadata.create_all(bind=engine)
model_category.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(category.router)
