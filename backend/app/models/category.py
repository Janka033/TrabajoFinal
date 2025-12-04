from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core import Base


class Category(Base):
    """
    Clase que representa una categoría en el inventario.
    Hecha por un estudiante: guarda el nombre y
    se relaciona con muchos productos.
    """
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    products = relationship(
        "Product",
        back_populates="category",
        cascade="all, delete-orphan",
    )
