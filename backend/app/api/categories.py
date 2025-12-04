from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core import SessionLocal
from app.schemas.category import CategoryCreate, CategoryRead
from app.services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=CategoryRead, status_code=201)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    service = CategoryService(db)
    return service.create(name=payload.name)


@router.get("/", response_model=list[CategoryRead])
def list_categories(db: Session = Depends(get_db)):
    service = CategoryService(db)
    return service.list()


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    service = CategoryService(db)
    ok = service.delete(category_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Category not found")
