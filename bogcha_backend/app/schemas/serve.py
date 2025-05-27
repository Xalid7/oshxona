from pydantic import BaseModel

class ServeMealRequest(BaseModel):
    meal_id: int

class MealPortionOut(BaseModel):
    meal_name: str
    portions: int
