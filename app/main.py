import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import init_db, SessionLocal
from app.services.source_verification import SourceVerificationService
from app.api.routes import health, medicines, alternatives, pricing, chat, sources, admin, kendras, catalogue, brands


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    init_db()
    # Seed default data sources
    with SessionLocal() as db:
        SourceVerificationService.ensure_default_sources(db)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "GenericMeds AI: AI-powered generic medicine discovery, composition equivalence, "
        "and verified price comparison platform for India (PMBI Jan Aushadhi & NPPA Pharma Sahi Daam)."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS Middleware
origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [settings.CORS_ORIGINS]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers for clean error responses
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log exception internally, don't leak stack traces
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred while processing the medicine inquiry.",
            "detail": str(exc) if settings.ENVIRONMENT == "development" else None,
        },
    )

# Include API routers
app.include_router(health.router)
app.include_router(medicines.router)
app.include_router(alternatives.router)
app.include_router(pricing.router)
app.include_router(chat.router)
app.include_router(sources.router)
app.include_router(admin.router)
app.include_router(kendras.router)
app.include_router(catalogue.router)
app.include_router(brands.router)

# Mount frontend static files if directory exists
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    assets_dir = os.path.join(static_dir, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.api_route("/favicon.svg", methods=["GET", "HEAD"], include_in_schema=False)
    def serve_favicon_svg():
        svg_path = os.path.join(static_dir, "favicon.svg")
        if os.path.exists(svg_path):
            return FileResponse(svg_path, media_type="image/svg+xml")
        return JSONResponse(status_code=404, content={"detail": "Favicon not found"})

    @app.api_route("/favicon.ico", methods=["GET", "HEAD"], include_in_schema=False)
    def serve_favicon_ico():
        svg_path = os.path.join(static_dir, "favicon.svg")
        if os.path.exists(svg_path):
            return FileResponse(svg_path, media_type="image/svg+xml")
        return JSONResponse(status_code=404, content={"detail": "Favicon not found"})

    @app.api_route("/", methods=["GET", "HEAD"], include_in_schema=False)
    def serve_frontend():
        return FileResponse(os.path.join(static_dir, "index.html"))
else:
    @app.api_route("/", methods=["GET", "HEAD"], include_in_schema=False)
    def home_redirect():
        return {
            "name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "documentation": "/docs",
            "health": "/health",
            "notice": "GenericMeds AI API is running. Visit /docs for interactive Swagger API testing.",
        }
