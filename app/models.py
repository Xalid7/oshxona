from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey, Text, DECIMAL, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    password_hash = Column(String(255))
    role = Column(String(20), default="cook")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    
    meal_servings = relationship("MealServing", back_populates="user")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    quantity = Column(Numeric(10, 3), default=0)
    unit = Column(String(20), default="g")
    minimum_quantity = Column(Numeric(10, 3), default=100)
    delivery_date = Column(Date)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    meal_ingredients = relationship("MealIngredient", back_populates="product")
    usage_logs = relationship("ProductUsageLog", back_populates="product")

class Meal(Base):
    __tablename__ = "meals"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    ingredients = relationship("MealIngredient", back_populates="meal")
    servings = relationship("MealServing", back_populates="meal")

class MealIngredient(Base):
    __tablename__ = "meal_ingredients"
    
    id = Column(Integer, primary_key=True, index=True)
    meal_id = Column(Integer, ForeignKey("meals.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Numeric(10, 3))
    unit = Column(String(20), default="g")
    
    meal = relationship("Meal", back_populates="ingredients")
    product = relationship("Product", back_populates="meal_ingredients")

class MealServing(Base):
    __tablename__ = "meal_servings"
    
    id = Column(Integer, primary_key=True, index=True)
    meal_id = Column(Integer, ForeignKey("meals.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    portions_served = Column(Integer)
    served_at = Column(DateTime, server_default=func.now())
    notes = Column(Text)
    
    meal = relationship("Meal", back_populates="servings")
    user = relationship("User", back_populates="meal_servings")
    usage_logs = relationship("ProductUsageLog", back_populates="meal_serving")

class ProductUsageLog(Base):
    __tablename__ = "product_usage_log"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    meal_serving_id = Column(Integer, ForeignKey("meal_servings.id"))
    quantity_used = Column(Numeric(10, 3))
    unit = Column(String(20), default="g")
    used_at = Column(DateTime, server_default=func.now())
    
    product = relationship("Product", back_populates="usage_logs")
    meal_serving = relationship("MealServing", back_populates="usage_logs")

class MonthlyReport(Base):
    __tablename__ = "monthly_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    month = Column(Integer)
    year = Column(Integer)
    total_portions_served = Column(Integer, default=0)
    total_portions_possible = Column(Integer, default=0)
    efficiency_percentage = Column(DECIMAL(5,2))
    is_suspicious = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
