from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core import SessionLocal
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"])


def get_db():
    """
    Devuelve una sesión de base de datos por petición.
    Hecho por un estudiante: abre y cierra la conexión correctamente.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=ProductRead, status_code=201)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    """
    Crea un producto usando los datos enviados.
    """
    service = ProductService(db)
    return service.create(**payload.model_dump())


@router.get("/", response_model=list[ProductRead])
def list_products(db: Session = Depends(get_db)):
    """
    Lista todos los productos guardados.
    """
    service = ProductService(db)
    return service.list()


@router.get("/{product_id}", response_model=ProductRead)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Obtiene un producto por su id o devuelve 404 si no existe.
    """
    service = ProductService(db)
    prod = service.get(product_id)
    if not prod:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )
    return prod


@router.put("/{product_id}", response_model=ProductRead)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
):
    """
    Actualiza un producto por id con los datos enviados.
    """
    service = ProductService(db)
    prod = service.update(
        product_id,
        **payload.model_dump(),
    )
    if not prod:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )
    return prod


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """
    Borra un producto por su id. Si no existe, devuelve 404.
    """
    service = ProductService(db)
    ok = service.delete(product_id)
    if not ok:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )
