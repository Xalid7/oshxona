from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.serve import ServeMealRequest, MealPortionOut
from app.database import get_db
from app.crud import serve, portions

router = APIRouter(prefix="/api", tags=["Serving"])

@router.post("/serve-meal/")
def serve_meal(request: ServeMealRequest, db: Session = Depends(get_db)):
    return serve.serve_meal(db, request)

@router.get("/meal-portions/", response_model=list[MealPortionOut])
def get_portions(db: Session = Depends(get_db)):
    return portions.calculate_portions(db)
