from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.routers import products, meals, servings, reports, auth, users
from app.database import engine, Base
from app.auth import get_current_user

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Kindergarten Management System", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(meals.router, prefix="/api/meals", tags=["Meals"])
app.include_router(servings.router, prefix="/api/servings", tags=["Servings"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])

@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
