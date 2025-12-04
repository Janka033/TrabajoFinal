from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core import SessionLocal
from app.schemas.category import CategoryCreate, CategoryRead
from app.services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])


def get_db():
    """
    Devuelve una sesión de base de datos por petición.
    Hecho por un estudiante: abre la conexión y se asegura de cerrarla.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=CategoryRead, status_code=201)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    """
    Crea una nueva categoría con el nombre enviado.
    """
    service = CategoryService(db)
    return service.create(name=payload.name)


@router.get("/", response_model=list[CategoryRead])
def list_categories(db: Session = Depends(get_db)):
    """
    Lista todas las categorías guardadas.
    """
    service = CategoryService(db)
    return service.list()


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """
    Borra una categoría por su id. Si no existe, devuelve 404.
    """
    service = CategoryService(db)
    ok = service.delete(category_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Category not found")


@router.put("/{category_id}", response_model=CategoryRead)
def update_category(category_id: int, payload: CategoryCreate, db: Session = Depends(get_db)):
    """
    Actualiza el nombre de la categoría.
    """
    service = CategoryService(db)
    cat = service.update(category_id, name=payload.name)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    return cat
