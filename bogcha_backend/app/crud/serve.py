from sqlalchemy.orm import Session
from app.models.meal import Meal
from app.models.ingredient import Ingredient
from app.models.serve import Serve
from app.schemas.serve import ServeMealRequest
from fastapi import HTTPException

def serve_meal(db: Session, request: ServeMealRequest):
    meal = db.query(Meal).filter(Meal.id == request.meal_id).first()
    if not meal:
        raise HTTPException(status_code=404, detail="Ovqat topilmadi")

    for item in meal.ingredients:
        ing = db.query(Ingredient).filter(Ingredient.name == item.name).first()
        if not ing or ing.quantity_grams < item.amount:
            raise HTTPException(status_code=400, detail=f"{item.name} yetarli emas")

    # Subtract ingredients
    for item in meal.ingredients:
        ing = db.query(Ingredient).filter(Ingredient.name == item.name).first()
        ing.quantity_grams -= item.amount
        db.add(ing)

    log = MealServeLog(meal_name=meal.name, served_by="Admin")  # foydalanuvchini aniqlash keyinchalik
    db.add(log)
    db.commit()
    return {"success": True}
