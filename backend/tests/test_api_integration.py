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


def test_update_category_name(client: TestClient):
    # Crear categoría
    r = client.post("/categories/", json={"name": "Inicial"})
    assert r.status_code == 201
    cat = r.json()

    # Actualizar nombre
    r2 = client.put(f"/categories/{cat['id']}", json={"name": "Actualizada"})
    assert r2.status_code == 200
    cat2 = r2.json()
    assert cat2["name"] == "Actualizada"

    # Verificar en listado
    r3 = client.get("/categories/")
    assert r3.status_code == 200
    cats = r3.json()
    assert any(c["id"] == cat["id"] and c["name"] == "Actualizada" for c in cats)


def test_get_category_by_id_route_not_implemented(client: TestClient):
    r = client.post("/categories/", json={"name": "ById"})
    assert r.status_code == 201
    cat = r.json()
    r2 = client.get(f"/categories/{cat['id']}")
    # Actualmente el API no implementa GET /categories/{id}
    assert r2.status_code == 405


def test_delete_category_existing_and_not_found(client: TestClient):
    r = client.post("/categories/", json={"name": "DelMe"})
    assert r.status_code == 201
    cat = r.json()
    r2 = client.delete(f"/categories/{cat['id']}")
    assert r2.status_code in (200, 204)
    r3 = client.delete("/categories/999999")
    assert r3.status_code == 404


def test_put_product_update_fields(client: TestClient):
    rc = client.post("/categories/", json={"name": "ForProd"})
    assert rc.status_code == 201
    cat = rc.json()
    rp = client.post(
        "/products/",
        json={
            "name": "Prod1",
            "description": "D",
            "price": 1.0,
            "stock": 1,
            "category_id": cat["id"],
        },
    )
    assert rp.status_code == 201
    prod = rp.json()
    ru = client.put(
        f"/products/{prod['id']}",
        json={"name": "Prod2", "description": "D2", "price": 2.0, "stock": 3},
    )
    assert ru.status_code == 200
    prod2 = ru.json()
    assert prod2["name"] == "Prod2" and prod2["price"] == 2.0 and prod2["stock"] == 3


def test_get_product_by_id_existing_and_not_found(client: TestClient):
    rc = client.post("/categories/", json={"name": "ForProdGet"})
    assert rc.status_code == 201
    cat = rc.json()
    rp = client.post(
        "/products/",
        json={
            "name": "ProdGet",
            "description": "D",
            "price": 1.0,
            "stock": 1,
            "category_id": cat["id"],
        },
    )
    assert rp.status_code == 201
    prod = rp.json()
    r2 = client.get(f"/products/{prod['id']}")
    assert r2.status_code == 200
    r3 = client.get("/products/999999")
    assert r3.status_code == 404


def test_post_product_invalid_category_current_behavior(client: TestClient):
    rp = client.post(
        "/products/",
        json={
            "name": "BadCat",
            "description": "",
            "price": 1.0,
            "stock": 1,
            "category_id": 999999,
        },
    )
    # Comportamiento actual: crea producto aunque el category_id no exista (sin validación estricta)
    assert rp.status_code == 201
