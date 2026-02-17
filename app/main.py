from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.database import db
from app.routes import auth_routes, resource_routes, review_routes, quote_routes, page_routes
from app.routes.quote_routes import seed_quotes
import os

app = FastAPI(title="EduHub", description="Educational Resource Sharing Platform")

# --- Static files & uploads ---
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
app.mount("/uploads", StaticFiles(directory=os.path.join(BASE_DIR, "uploads")), name="uploads")

# --- Include Routers ---
app.include_router(auth_routes.router)
app.include_router(resource_routes.router)
app.include_router(review_routes.router)
app.include_router(quote_routes.router)
app.include_router(page_routes.router)

# --- Startup ---
@app.on_event("startup")
def startup():
    os.makedirs(os.path.join(BASE_DIR, "uploads"), exist_ok=True)
    seed_quotes()
    print("🚀 EduHub is running!")