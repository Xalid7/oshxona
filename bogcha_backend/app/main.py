from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.api import ingredient, dashboard, meal, serve
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# 📁 Static fayllar
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
TEMPLATES_DIR = BASE_DIR
app.mount("/static", StaticFiles(directory=ASSETS_DIR), name="static")
app.mount("/frontend", StaticFiles(directory=TEMPLATES_DIR, html=True), name="frontend")

# 🛠 DB
Base.metadata.create_all(bind=engine)

# 🌍 Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔗 Routers
app.include_router(ingredient.router, prefix="/api/ingredients")
app.include_router(dashboard.router, prefix="/api")
app.include_router(meal.router, prefix="/api")
app.include_router(serve.router, prefix="/api")
