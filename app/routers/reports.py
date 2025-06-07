from http.client import HTTPException
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.database import get_db
from app.models import MealServing, MonthlyReport, Product, ProductUsageLog, User
from app.schemas import MonthlyReportResponse
from app.auth import get_current_user, require_role
from datetime import datetime, date

router = APIRouter()

@router.get("/monthly", response_model=List[MonthlyReportResponse])
async def get_monthly_reports(
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_role(["admin", "manager"]))
):
    reports = db.query(MonthlyReport).order_by(MonthlyReport.year.desc(), MonthlyReport.month.desc()).all()
    return reports


@router.post("/generate-monthly/{year}/{month}")
async def generate_monthly_report(
        year: int,
        month: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(require_role(["admin", "manager"]))
):
    # Check if report already exists
    existing_report = db.query(MonthlyReport).filter(
        MonthlyReport.year == year,
        MonthlyReport.month == month
    ).first()

    if existing_report:
        db.delete(existing_report)
        db.commit()  # delete ni saqlash

    # Calculate total portions served in the month
    total_served = db.query(func.sum(MealServing.portions_served)).filter(
        extract('year', MealServing.served_at) == year,
        extract('month', MealServing.served_at) == month
    ).scalar() or 0

    # Calculate total possible portions (simplified calculation)
    total_possible = total_served + int(total_served * 0.2)  # Assume 20% more could have been made

    # Calculate efficiency percentage
    efficiency = (total_served / total_possible * 100) if total_possible > 0 else 0

    # Check if suspicious (more than 15% difference)
    is_suspicious = abs(100 - efficiency) > 15

    # Create new report
    new_report = MonthlyReport(
        month=month,
        year=year,
        total_portions_served=total_served,
        total_portions_possible=total_possible,
        efficiency_percentage=efficiency,
        is_suspicious=is_suspicious
    )

    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    return new_report


@router.get("/dashboard-stats")
async def get_dashboard_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    today = date.today()
    
    # Today's servings
    today_servings = db.query(func.sum(MealServing.portions_served)).filter(
        func.date(MealServing.served_at) == today
    ).scalar() or 0
    
    # Low stock products
    low_stock_count = db.query(Product).filter(
        Product.quantity_grams <= Product.minimum_quantity
    ).count()
    
    # Total products
    total_products = db.query(Product).count()
    
    # Recent servings
    recent_servings = db.query(MealServing).order_by(
        MealServing.served_at.desc()
    ).limit(5).all()
    
    return {
        "today_servings": today_servings,
        "low_stock_count": low_stock_count,
        "total_products": total_products,
        "recent_servings": len(recent_servings)
    }

@router.get("/usage-analytics")
async def get_usage_analytics(
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_role(["admin", "manager"]))
):
    # Get usage data for the last 30 days
    from datetime import timedelta
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    usage_data = db.query(
        Product.name,
        func.sum(ProductUsageLog.quantity_used).label('total_used')
    ).join(ProductUsageLog).filter(
        ProductUsageLog.used_at >= thirty_days_ago
    ).group_by(Product.name).all()
    
    return [{"product": item.name, "usage": item.total_used} for item in usage_data]
