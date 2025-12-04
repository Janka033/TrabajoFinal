from pydantic import BaseModel, ConfigDict


class CategoryCreate(BaseModel):
    name: str


class CategoryRead(BaseModel):
    id: int
    name: str

    # Pydantic v2 config
    model_config = ConfigDict(from_attributes=True)
