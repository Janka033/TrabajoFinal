import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core import Base
from app.services.category_service import CategoryService
from app.services.product_service import ProductService

@pytest.fixture()
def db_session():
    # Use SQLite in-memory for unit tests of services
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

def test_category_crud(db_session):
    cs = CategoryService(db_session)
    c = cs.create("Bebidas")
    assert c.id > 0
    assert cs.list()[0].name == "Bebidas"
    assert cs.delete(c.id) is True

def test_product_crud(db_session):
    cs = CategoryService(db_session)
    c = cs.create("Snacks")
    ps = ProductService(db_session)
    p = ps.create(name="Papas", description="Con sal", price=2.5, stock=10, category_id=c.id)
    assert p.id > 0
    p2 = ps.update(p.id, price=3.0)
    assert p2.price == 3.0
    assert ps.delete(p.id) is True
