from fastapi import APIRouter

router = APIRouter( tags=["Stats"])  # ❗ prefix BOR

@router.get("/monthly")
def monthly():
    return {"prepared_portions": 100, "possible_portions": 150}

@router.get("/consumption")
def consumption():
    return {"labels": ["Go‘sht", "Piyoz"], "data": [4.2, 2.5]}

@router.get("/delivery")
def delivery():
    return {"labels": ["2024-05-25"], "data": [10]}
