from sqlalchemy.orm import Session
from app.models.meal import Meal, MealIngredient
from app.models.ingredient import Ingredient
from app.schemas.meal import MealCreate

def create_meal(db: Session, meal_data: MealCreate):
    meal = Meal(name=meal_data.name)
    db.add(meal)
    db.flush()  # id olish uchun

    for item in meal_data.ingredients:
        db.add(MealIngredient(
            meal_id=meal.id,
            ingredient_id=item.ingredient_id,
            amount_grams=item.amount_grams
        ))
    db.commit()
    db.refresh(meal)
    return meal

def get_meals(db: Session):
    return db.query(Meal).all()

def get_meal(db: Session, meal_id: int):
    return db.query(Meal).filter(Meal.id == meal_id).first()

def delete_meal(db: Session, meal_id: int):
    meal = get_meal(db, meal_id)
    if meal:
        db.delete(meal)
        db.commit()
