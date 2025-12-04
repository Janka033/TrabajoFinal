from pydantic import BaseModel, Field
from pydantic import ConfigDict


class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price: float = Field(gt=0)
    stock: int = Field(ge=0)
    category_id: int


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = Field(default=None, gt=0)
    stock: int | None = Field(default=None, ge=0)
    category_id: int | None = None


class ProductRead(BaseModel):
    id: int
    name: str
    description: str | None
    price: float
    stock: int
    category_id: int

    # Pydantic v2 config
    model_config = ConfigDict(from_attributes=True)
    
