from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import MealServing, Meal, Product, MealIngredient, ProductUsageLog, User
from app.schemas import MealServingCreate, MealServingResponse
from app.auth import get_current_user

router = APIRouter()

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
        required_quantity = ingredient.quantity_grams * serving.portions_served
        
        if not product or product.quantity_grams < required_quantity:
            raise HTTPException(
                status_code=400, 
                detail=f"Not enough {product.name if product else 'ingredient'} available. Required: {required_quantity}g, Available: {product.quantity_grams if product else 0}g"
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
        used_quantity = ingredient.quantity_grams * serving.portions_served
        
        # Update product quantity
        product.quantity_grams -= used_quantity
        
        # Log usage
        usage_log = ProductUsageLog(
            product_id=product.id,
            meal_serving_id=db_serving.id,
            quantity_used=used_quantity
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
