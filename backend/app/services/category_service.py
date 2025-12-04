from sqlalchemy.orm import Session
from app.models.category import Category


class CategoryService:
    """
    Servicio para manejar categorías.
    Hecho por un estudiante: crea, lista, busca y borra categorías
    usando la base de datos con SQLAlchemy.
    """
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str) -> Category:
        cat = Category(name=name)
        self.db.add(cat)
        self.db.commit()
        self.db.refresh(cat)
        return cat

    def list(self) -> list[Category]:
        return self.db.query(Category).all()

    def get(self, category_id: int) -> Category | None:
        return self.db.get(Category, category_id)

    def delete(self, category_id: int) -> bool:
        cat = self.get(category_id)
        if not cat:
            return False
        self.db.delete(cat)
        self.db.commit()
        return True
