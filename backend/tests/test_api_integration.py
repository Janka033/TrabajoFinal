import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core import Base
# Ensure models are imported so metadata has all tables
from app.models import category as _category_model  # noqa: F401
from app.models import product as _product_model  # noqa: F401
from app.api.categories import (
    router as categories_router,
    get_db as categories_get_db,
)
from app.api.products import (
    router as products_router,
    get_db as products_get_db,
)


# Create a FastAPI app for tests using SQLite in-memory
engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    future=True,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
Base.metadata.create_all(bind=engine)


def get_test_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_test_app() -> FastAPI:
    app = FastAPI()
    app.include_router(categories_router, dependencies=[Depends(get_test_db)])
    app.include_router(products_router, dependencies=[Depends(get_test_db)])
    # Explicitly override per-router get_db dependencies
    app.dependency_overrides[categories_get_db] = get_test_db
    app.dependency_overrides[products_get_db] = get_test_db
    return app


@pytest.fixture(scope="module")
def client():
    app = create_test_app()
    return TestClient(app)


def test_flow_create_category_and_product_listing(client: TestClient):
    r = client.post("/categories/", json={"name": "Lacteos"})
    assert r.status_code == 201
    cat = r.json()

    r2 = client.post(
        "/products/",
        json={
            "name": "Leche",
            "description": "Entera",
            "price": 1.99,
            "stock": 20,
            "category_id": cat["id"],
        },
    )
    assert r2.status_code == 201

    r3 = client.get("/products/")
    assert r3.status_code == 200
    products = r3.json()
    assert any(p["name"] == "Leche" for p in products)
