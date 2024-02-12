from fastapi import FastAPI
from database import engine
from models import model_category, model_user, model_product, model_cart
from routers import category, auth, product, permission, user_profile


app = FastAPI()

model_user.Base.metadata.create_all(bind=engine)
model_category.Base.metadata.create_all(bind=engine)
model_product.Base.metadata.create_all(bind=engine)
model_cart.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(category.router)
app.include_router(product.router)
app.include_router(permission.router)
app.include_router(user_profile.router)
