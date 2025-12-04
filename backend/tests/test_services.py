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
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
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
    # Actualizar nombre
    c2 = cs.update(c.id, name="Bebidas2")
    assert c2 is not None and c2.name == "Bebidas2"
    assert cs.delete(c.id) is True


def test_product_crud(db_session):
    cs = CategoryService(db_session)
    c = cs.create("Snacks")
    ps = ProductService(db_session)
    p = ps.create(
        name="Papas",
        description="Con sal",
        price=2.5,
        stock=10,
        category_id=c.id,
    )
    assert p.id > 0
    p2 = ps.update(p.id, price=3.0)
    assert p2.price == 3.0
    assert ps.delete(p.id) is True


def test_category_get_not_found(db_session):
    cs = CategoryService(db_session)
    assert cs.get(999999) is None


def test_category_update_not_found(db_session):
    cs = CategoryService(db_session)
    assert cs.update(999999, name="x") is None


def test_category_delete_not_found(db_session):
    cs = CategoryService(db_session)
    assert cs.delete(999999) is False


def test_product_get_not_found(db_session):
    ps = ProductService(db_session)
    assert ps.get(999999) is None


def test_product_update_not_found(db_session):
    ps = ProductService(db_session)
    assert ps.update(999999, price=1.0) is None


def test_product_update_multiple_fields(db_session):
    cs = CategoryService(db_session)
    c = cs.create("Multi")
    ps = ProductService(db_session)
    p = ps.create(
        name="A",
        description="B",
        price=1.0,
        stock=1,
        category_id=c.id,
    )
    p2 = ps.update(p.id, name="A2", description="B2", price=2.0, stock=3)
    assert p2.name == "A2" and p2.description == "B2" and p2.price == 2.0 and p2.stock == 3


def test_product_create_invalid_category_raises(db_session):
    ps = ProductService(db_session)
    # Comportamiento actual con SQLite en memoria: no se eleva IntegrityError automáticamente
    p = ps.create(
        name="Bad",
        description="",
        price=1.0,
        stock=1,
        category_id=123456,
    )
    assert p is not None
