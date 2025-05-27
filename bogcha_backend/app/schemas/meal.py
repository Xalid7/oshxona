from pydantic import BaseModel
from typing import List

class MealIngredientCreate(BaseModel):
    ingredient_id: int
    amount_grams: float

class MealBase(BaseModel):
    name: str

class MealCreate(MealBase):
    ingredients: List[MealIngredientCreate]

class MealIngredientOut(BaseModel):
    ingredient_id: int
    amount_grams: float

    class Config:
        orm_mode = True

class MealOut(MealBase):
    id: int
    ingredients: List[MealIngredientOut]

    class Config:
        orm_mode = True
