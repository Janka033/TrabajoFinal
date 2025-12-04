import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core import Base
from app.models.category import Category
from app.models.product import Product

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "inventario")
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def run():
    session = SessionLocal()
    try:
        # Seed categories
        bebidas = Category(name="Bebidas")
        snacks = Category(name="Snacks")
        session.add_all([bebidas, snacks])
        session.flush()
        # Seed products
        p1 = Product(name="Agua", description="Botella 600ml", price=1.2, stock=100, category_id=bebidas.id)
        p2 = Product(name="Papas", description="Clásicas", price=2.5, stock=50, category_id=snacks.id)
        session.add_all([p1, p2])
        session.commit()
        print("Seed completado")
    except Exception as e:
        session.rollback()
        print("Seed falló:", e)
    finally:
        session.close()


if __name__ == "__main__":
    run()
