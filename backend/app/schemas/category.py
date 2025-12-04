from pydantic import BaseModel, ConfigDict


class CategoryCreate(BaseModel):
    """Datos para crear una categoría (solo nombre)."""
    name: str


class CategoryRead(BaseModel):
    """Datos que se devuelven al leer una categoría."""
    id: int
    name: str

    # Configuración de Pydantic v2 para leer desde objetos ORM
    model_config = ConfigDict(from_attributes=True)
