from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, date

# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: str = "cook"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Product schemas
class ProductBase(BaseModel):
    name: str
    quantity: float
    unit: str = "g"
    minimum_quantity: float = 100
    delivery_date: Optional[date] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    minimum_quantity: Optional[float] = None
    delivery_date: Optional[date] = None

class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Meal schemas
class MealIngredientBase(BaseModel):
    product_id: int
    quantity: float
    unit: str = "g"

class MealIngredientResponse(MealIngredientBase):
    id: int
    product_name: str
    
    class Config:
        from_attributes = True

class MealBase(BaseModel):
    name: str
    description: Optional[str] = None

class MealCreate(MealBase):
    ingredients: List[MealIngredientBase]

class MealUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    ingredients: Optional[List[MealIngredientBase]] = None

class MealResponse(MealBase):
    id: int
    is_active: bool
    created_at: datetime
    ingredients: List[MealIngredientResponse] = []
    possible_portions: int = 0
    
    class Config:
        from_attributes = True

# Serving schemas
class MealServingCreate(BaseModel):
    meal_id: int
    portions_served: int
    notes: Optional[str] = None

class MealServingResponse(BaseModel):
    id: int
    meal_id: int
    meal_name: str
    user_id: int
    username: str
    portions_served: int
    served_at: datetime
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True

# Report schemas
class MonthlyReportResponse(BaseModel):
    id: int
    month: int
    year: int
    total_portions_served: int
    total_portions_possible: int
    efficiency_percentage: float
    is_suspicious: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    username: str
    password: str
