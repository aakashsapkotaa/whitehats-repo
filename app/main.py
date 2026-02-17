from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.database import db
from app.routes import auth_routes, resource_routes, review_routes, quote_routes, page_routes
from app.routes import token_routes, community_routes, ocr_routes, admin_routes, group_routes
from app.routes.quote_routes import seed_quotes
import os

app = FastAPI(title="EduHub", description="Educational Resource Sharing Platform")

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Rate Limiting ---
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded

    limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
except ImportError:
    print("⚠️  slowapi not installed — rate limiting disabled")

# --- Static files & uploads ---
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
app.mount("/uploads", StaticFiles(directory=os.path.join(BASE_DIR, "uploads")), name="uploads")

# --- Include Routers ---
app.include_router(auth_routes.router)
app.include_router(resource_routes.router)
app.include_router(review_routes.router)
app.include_router(quote_routes.router)
app.include_router(token_routes.router)
app.include_router(community_routes.router)
app.include_router(ocr_routes.router)
app.include_router(admin_routes.router)
app.include_router(group_routes.router)
app.include_router(page_routes.router)

# --- Startup ---
@app.on_event("startup")
def startup():
    os.makedirs(os.path.join(BASE_DIR, "uploads"), exist_ok=True)
    seed_quotes()
    print("🚀 EduHub is running!")