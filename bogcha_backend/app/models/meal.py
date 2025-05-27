from sqlalchemy import Column, Integer, String, ForeignKey, Float, Table
from sqlalchemy.orm import relationship
from app.database import Base

class MealIngredient(Base):
    __tablename__ = "meal_ingredients"

    meal_id = Column(Integer, ForeignKey("meals.id"), primary_key=True)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), primary_key=True)
    amount_grams = Column(Float, nullable=False)

class Meal(Base):
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    ingredients = relationship(
        "MealIngredient",
        backref="meal",
        cascade="all, delete"
    )
