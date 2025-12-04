import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_flow_create_category_and_product_listing():
    # create category
    r = client.post("/categories/", json={"name": "Lacteos"})
    assert r.status_code == 201
    cat = r.json()

    # create product
    r2 = client.post("/products/", json={
        "name": "Leche",
        "description": "Entera",
        "price": 1.99,
        "stock": 20,
        "category_id": cat["id"],
    })
    assert r2.status_code == 201

    # list products
    r3 = client.get("/products/")
    assert r3.status_code == 200
    products = r3.json()
    assert any(p["name"] == "Leche" for p in products)
