from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.ingredient import IngredientCreate, IngredientUpdate, IngredientInDB
from app.crud import ingredient as crud
from app.database import get_db

router = APIRouter(tags=["Ingredients"])


@router.get("/", response_model=list[IngredientInDB])
def list_ingredients(db: Session = Depends(get_db)):
    return crud.get_all(db)

@router.post("/", response_model=IngredientInDB)
def create_ingredient(data: IngredientCreate, db: Session = Depends(get_db)):
    return crud.create(db, data)

@router.get("/{ingredient_id}", response_model=IngredientInDB)
def get_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
    obj = crud.get_one(db, ingredient_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return obj

@router.put("/{ingredient_id}", response_model=IngredientInDB)
def update_ingredient(ingredient_id: int, data: IngredientUpdate, db: Session = Depends(get_db)):
    obj = crud.update(db, ingredient_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return obj

@router.delete("/{ingredient_id}")
def delete_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
    obj = crud.delete(db, ingredient_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return {"detail": "Deleted"}
