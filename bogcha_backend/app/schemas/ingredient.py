
from pydantic import BaseModel
from datetime import date
from typing import Optional

class IngredientBase(BaseModel):
    name: str
    quantity: float  # ✅ majburiy!
    delivered_at: Optional[date] = None  # ✅ optional


class IngredientCreate(BaseModel):
    name: str
    quantity: float
    delivered_at: Optional[date] = None

class IngredientUpdate(IngredientBase):
    pass

class IngredientInDB(IngredientBase):
    id: int

    class Config:
        orm_mode = True
