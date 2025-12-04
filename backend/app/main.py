from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core import Base, engine
from app.api.categories import router as categories_router
from app.api.products import router as products_router

app = FastAPI(title="Inventario API")

# Create tables if not exist (for simplicity). In production, use Alembic.
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(categories_router)
app.include_router(products_router)


@app.get("/health")
def health():
    return {"status": "ok"}
