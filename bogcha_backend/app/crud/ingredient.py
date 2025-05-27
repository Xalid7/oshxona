from sqlalchemy.orm import Session
from app.models.ingredient import Ingredient
from app.schemas.ingredient import IngredientCreate, IngredientUpdate

def get_all(db: Session):
    return db.query(Ingredient).all()

def get_one(db: Session, ingredient_id: int):
    return db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()

def create(db: Session, data: IngredientCreate):
    obj = Ingredient(**data.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def update(db: Session, ingredient_id: int, data: IngredientUpdate):
    obj = get_one(db, ingredient_id)
    if obj:
        for field, value in data.dict().items():
            setattr(obj, field, value)
        db.commit()
        db.refresh(obj)
    return obj

def delete(db: Session, ingredient_id: int):
    obj = get_one(db, ingredient_id)
    if obj:
        db.delete(obj)
        db.commit()
    return obj
