from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Meal, MealIngredient, Product, User
from app.schemas import MealCreate, MealUpdate, MealResponse, MealIngredientResponse
from app.auth import get_current_user, require_role

router = APIRouter()

def calculate_possible_portions(meal: Meal, db: Session) -> int:
    """Calculate how many portions can be made from available ingredients"""
    if not meal.ingredients:
        return 0
    
    min_portions = float('inf')
    for ingredient in meal.ingredients:
        product = db.query(Product).filter(Product.id == ingredient.product_id).first()
        if product and product.quantity_grams > 0:
            possible_portions = product.quantity_grams // ingredient.quantity_grams
            min_portions = min(min_portions, possible_portions)
        else:
            return 0
    
    return int(min_portions) if min_portions != float('inf') else 0

@router.get("/", response_model=List[MealResponse])
async def get_meals(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    meals = db.query(Meal).filter(Meal.is_active == True).all()
    result = []
    
    for meal in meals:
        meal_dict = {
            "id": meal.id,
            "name": meal.name,
            "description": meal.description,
            "is_active": meal.is_active,
            "created_at": meal.created_at,
            "ingredients": [],
            "possible_portions": calculate_possible_portions(meal, db)
        }
        
        for ingredient in meal.ingredients:
            product = db.query(Product).filter(Product.id == ingredient.product_id).first()
            meal_dict["ingredients"].append({
                "id": ingredient.id,
                "product_id": ingredient.product_id,
                "quantity_grams": ingredient.quantity_grams,
                "product_name": product.name if product else "Unknown"
            })
        
        result.append(meal_dict)
    
    return result

@router.get("/{meal_id}", response_model=MealResponse)
async def get_meal(meal_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    meal = db.query(Meal).filter(Meal.id == meal_id).first()
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    
    meal_dict = {
        "id": meal.id,
        "name": meal.name,
        "description": meal.description,
        "is_active": meal.is_active,
        "created_at": meal.created_at,
        "ingredients": [],
        "possible_portions": calculate_possible_portions(meal, db)
    }
    
    for ingredient in meal.ingredients:
        product = db.query(Product).filter(Product.id == ingredient.product_id).first()
        meal_dict["ingredients"].append({
            "id": ingredient.id,
            "product_id": ingredient.product_id,
            "quantity_grams": ingredient.quantity_grams,
            "product_name": product.name if product else "Unknown"
        })
    
    return meal_dict

@router.post("/", response_model=MealResponse)
async def create_meal(
    meal: MealCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_role(["admin", "manager"]))
):
    # Create meal
    db_meal = Meal(name=meal.name, description=meal.description)
    db.add(db_meal)
    db.commit()
    db.refresh(db_meal)
    
    # Add ingredients
    for ingredient in meal.ingredients:
        db_ingredient = MealIngredient(
            meal_id=db_meal.id,
            product_id=ingredient.product_id,
            quantity_grams=ingredient.quantity_grams
        )
        db.add(db_ingredient)
    
    db.commit()
    
    # Return meal with ingredients
    return await get_meal(db_meal.id, db, current_user)

@router.put("/{meal_id}", response_model=MealResponse)
async def update_meal(
    meal_id: int, 
    meal_update: MealUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "manager"]))
):
    db_meal = db.query(Meal).filter(Meal.id == meal_id).first()
    if not db_meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    
    # Update meal basic info
    if meal_update.name is not None:
        db_meal.name = meal_update.name
    if meal_update.description is not None:
        db_meal.description = meal_update.description
    if meal_update.is_active is not None:
        db_meal.is_active = meal_update.is_active
    
    # Update ingredients if provided
    if meal_update.ingredients is not None:
        # Delete existing ingredients
        db.query(MealIngredient).filter(MealIngredient.meal_id == meal_id).delete()
        
        # Add new ingredients
        for ingredient in meal_update.ingredients:
            db_ingredient = MealIngredient(
                meal_id=meal_id,
                product_id=ingredient.product_id,
                quantity_grams=ingredient.quantity_grams
            )
            db.add(db_ingredient)
    
    db.commit()
    return await get_meal(meal_id, db, current_user)

@router.delete("/{meal_id}")
async def delete_meal(
    meal_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    db_meal = db.query(Meal).filter(Meal.id == meal_id).first()
    if not db_meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    
    db.delete(db_meal)
    db.commit()
    return {"message": "Meal deleted successfully"}
