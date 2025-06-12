from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import MealServing, Meal, Product, MealIngredient, ProductUsageLog, User
from app.schemas import MealServingCreate, MealServingResponse
from app.auth import get_current_user

router = APIRouter()

def convert_to_base_unit(quantity: float, unit: str) -> float:
    """Convert quantity to base unit (grams for weight, ml for volume)"""
    conversions = {
        'g': 1,
        'kg': 1000,
        'ml': 1,
        'l': 1000,
        'dona': 1,
        'paket': 1,
        'quti': 1
    }
    return quantity * conversions.get(unit, 1)

def can_deduct_quantity(product_quantity: float, product_unit: str, needed_quantity: float, needed_unit: str) -> bool:
    """Check if we can deduct the needed quantity from available product"""
    # For weight/volume units, convert and compare
    if product_unit in ['g', 'kg'] and needed_unit in ['g', 'kg']:
        product_base = convert_to_base_unit(product_quantity, product_unit)
        needed_base = convert_to_base_unit(needed_quantity, needed_unit)
        return product_base >= needed_base
    elif product_unit in ['ml', 'l'] and needed_unit in ['ml', 'l']:
        product_base = convert_to_base_unit(product_quantity, product_unit)
        needed_base = convert_to_base_unit(needed_quantity, needed_unit)
        return product_base >= needed_base
    # For discrete units, units must match
    elif product_unit == needed_unit and product_unit in ['dona', 'paket', 'quti']:
        return product_quantity >= needed_quantity
    else:
        return False

def deduct_quantity(product_quantity: float, product_unit: str, needed_quantity: float, needed_unit: str) -> float:
    """Deduct needed quantity from product quantity and return new quantity in product's unit"""
    if product_unit in ['g', 'kg'] and needed_unit in ['g', 'kg']:
        product_base = convert_to_base_unit(product_quantity, product_unit)
        needed_base = convert_to_base_unit(needed_quantity, needed_unit)
        new_base = product_base - needed_base
        # Convert back to product's unit
        if product_unit == 'kg':
            return new_base / 1000
        else:
            return new_base
    elif product_unit in ['ml', 'l'] and needed_unit in ['ml', 'l']:
        product_base = convert_to_base_unit(product_quantity, product_unit)
        needed_base = convert_to_base_unit(needed_quantity, needed_unit)
        new_base = product_base - needed_base
        # Convert back to product's unit
        if product_unit == 'l':
            return new_base / 1000
        else:
            return new_base
    elif product_unit == needed_unit:
        return product_quantity - needed_quantity
    else:
        return product_quantity

@router.post("/", response_model=MealServingResponse)
async def serve_meal(
    serving: MealServingCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    # Get meal and check if it exists
    meal = db.query(Meal).filter(Meal.id == serving.meal_id).first()
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    
    # Check if enough ingredients are available
    for ingredient in meal.ingredients:
        product = db.query(Product).filter(Product.id == ingredient.product_id).first()
        required_quantity = float(ingredient.quantity) * serving.portions_served
        
        if not product:
            raise HTTPException(status_code=400, detail=f"Product not found for ingredient")
        
        if not can_deduct_quantity(float(product.quantity), product.unit, required_quantity, ingredient.unit):
            raise HTTPException(
                status_code=400, 
                detail=f"Not enough {product.name} available. Required: {required_quantity}{ingredient.unit}, Available: {product.quantity}{product.unit}"
            )
    
    # Create meal serving record
    db_serving = MealServing(
        meal_id=serving.meal_id,
        user_id=current_user.id,
        portions_served=serving.portions_served,
        notes=serving.notes
    )
    db.add(db_serving)
    db.commit()
    db.refresh(db_serving)
    
    # Deduct ingredients from inventory and log usage
    for ingredient in meal.ingredients:
        product = db.query(Product).filter(Product.id == ingredient.product_id).first()
        used_quantity = float(ingredient.quantity) * serving.portions_served
        
        # Update product quantity
        product.quantity = deduct_quantity(
            float(product.quantity), product.unit,
            used_quantity, ingredient.unit
        )
        
        # Log usage
        usage_log = ProductUsageLog(
            product_id=product.id,
            meal_serving_id=db_serving.id,
            quantity_used=used_quantity,
            unit=ingredient.unit
        )
        db.add(usage_log)
    
    db.commit()
    
    # Return serving with meal and user info
    return {
        "id": db_serving.id,
        "meal_id": db_serving.meal_id,
        "meal_name": meal.name,
        "user_id": db_serving.user_id,
        "username": current_user.username,
        "portions_served": db_serving.portions_served,
        "served_at": db_serving.served_at,
        "notes": db_serving.notes
    }

@router.get("/", response_model=List[MealServingResponse])
async def get_servings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    servings = db.query(MealServing).order_by(MealServing.served_at.desc()).limit(100).all()
    result = []
    
    for serving in servings:
        meal = db.query(Meal).filter(Meal.id == serving.meal_id).first()
        user = db.query(User).filter(User.id == serving.user_id).first()
        
        result.append({
            "id": serving.id,
            "meal_id": serving.meal_id,
            "meal_name": meal.name if meal else "Unknown",
            "user_id": serving.user_id,
            "username": user.username if user else "Unknown",
            "portions_served": serving.portions_served,
            "served_at": serving.served_at,
            "notes": serving.notes
        })
    
    return result

@router.get("/today", response_model=List[MealServingResponse])
async def get_today_servings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from datetime import date
    today = date.today()
    
    servings = db.query(MealServing).filter(
        MealServing.served_at >= today
    ).order_by(MealServing.served_at.desc()).all()
    
    result = []
    for serving in servings:
        meal = db.query(Meal).filter(Meal.id == serving.meal_id).first()
        user = db.query(User).filter(User.id == serving.user_id).first()
        
        result.append({
            "id": serving.id,
            "meal_id": serving.meal_id,
            "meal_name": meal.name if meal else "Unknown",
            "user_id": serving.user_id,
            "username": user.username if user else "Unknown",
            "portions_served": serving.portions_served,
            "served_at": serving.served_at,
            "notes": serving.notes
        })
    
    return result
