from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.meal import MealCreate, MealOut
from app.crud import meal as crud_meal
from app.database import get_db

router = APIRouter(prefix="/meals", tags=["Meals"])

@router.post("/", response_model=MealOut)
def create_meal(meal: MealCreate, db: Session = Depends(get_db)):
    return crud_meal.create_meal(db, meal)

@router.get("/", response_model=list[MealOut])
def read_meals(db: Session = Depends(get_db)):
    return crud_meal.get_meals(db)

@router.get("/{meal_id}", response_model=MealOut)
def read_meal(meal_id: int, db: Session = Depends(get_db)):
    db_meal = crud_meal.get_meal(db, meal_id)
    if not db_meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    return db_meal

@router.delete("/{meal_id}")
def delete_meal(meal_id: int, db: Session = Depends(get_db)):
    crud_meal.delete_meal(db, meal_id)
    return {"message": "Meal deleted"}
