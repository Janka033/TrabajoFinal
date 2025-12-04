from sqlalchemy.orm import Session
from app.models.product import Product

class ProductService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs) -> Product:
        prod = Product(**kwargs)
        self.db.add(prod)
        self.db.commit()
        self.db.refresh(prod)
        return prod

    def list(self) -> list[Product]:
        return self.db.query(Product).all()

    def get(self, product_id: int) -> Product | None:
        return self.db.query(Product).get(product_id)

    def update(self, product_id: int, **kwargs) -> Product | None:
        prod = self.get(product_id)
        if not prod:
            return None
        for k, v in kwargs.items():
            if v is not None:
                setattr(prod, k, v)
        self.db.commit()
        self.db.refresh(prod)
        return prod

    def delete(self, product_id: int) -> bool:
        prod = self.get(product_id)
        if not prod:
            return False
        self.db.delete(prod)
        self.db.commit()
        return True
