from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core import Base, engine
from app.api.categories import router as categories_router
from app.api.products import router as products_router

app = FastAPI()
"""
Aplicación principal FastAPI del proyecto.
Hecha por un estudiante: configura CORS, crea tablas,
expone un endpoint de salud y registra los routers.
"""

# CORS para permitir el frontend (incluye file:// y varios orígenes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"]
)

# Crear tablas al iniciar
Base.metadata.create_all(bind=engine)


# Health check
@app.get("/health")
def health():
    return {"status": "ok"}


# Incluir routers
app.include_router(categories_router)
app.include_router(products_router)
