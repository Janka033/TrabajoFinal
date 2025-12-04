from fastapi import FastAPI
from app.core import Base, engine
# importa tus routers
from app.api.categories import router as categories_router
from app.api.products import router as products_router

app = FastAPI()

# Crear tablas al iniciar
Base.metadata.create_all(bind=engine)

# Incluir routers
app.include_router(categories_router)
app.include_router(products_router)