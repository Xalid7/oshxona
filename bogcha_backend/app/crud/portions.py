from sqlalchemy.orm import Session
from app.models.meal import Meal
from app.models.ingredient import Ingredient

def calculate_portions(db: Session):
    meals = db.query(Meal).all()
    result = []

    for meal in meals:
        counts = []
        for i in meal.ingredients:
            ing = db.query(Ingredient).filter(Ingredient.name == i.name).first()
            if not ing or ing.quantity_grams < i.amount:
                counts.append(0)
            else:
                counts.append(ing.quantity_grams // i.amount)
        result.append({
            "meal_name": meal.name,
            "portions": min(counts) if counts else 0
        })

    return result
