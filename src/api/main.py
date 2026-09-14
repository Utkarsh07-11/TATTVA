"""FastAPI application for SIH 2026 PS 26009."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from config.settings import settings
from src.api.deps import get_forecaster, get_optimizer, get_prospectivity_model, get_shap_engine, runtime_status
from src.api.routes import forecast, explain, recommend, prospectivity, mine, real_data, demo

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        get_forecaster()
        get_prospectivity_model()
        get_shap_engine()
        get_optimizer()
        print("[FastAPI] Inference pipelines ready.")
    except Exception as exc:
        print(f"[FastAPI] Models will load on demand: {exc}")
    yield


# Disable interactive API docs in production to prevent schema/endpoint disclosure
docs_url = "/docs" if settings.ENVIRONMENT.lower() != "production" else None
redoc_url = "/redoc" if settings.ENVIRONMENT.lower() != "production" else None

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Manganese reserve identification and production-shortfall decision support.",
    lifespan=lifespan,
    docs_url=docs_url,
    redoc_url=redoc_url,
)

# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    return response


# Explicit CORS allowlist - prevents unauthorized cross-origin requests with credentials
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

api_prefix = settings.API_V1_STR
app.include_router(forecast.router, prefix=api_prefix)
app.include_router(explain.router, prefix=api_prefix)
app.include_router(recommend.router, prefix=api_prefix)
app.include_router(prospectivity.router, prefix=api_prefix)
app.include_router(mine.router, prefix=api_prefix)
app.include_router(real_data.router, prefix=api_prefix)
app.include_router(demo.router, prefix=api_prefix)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    
    logger.exception("Unhandled server exception at %s: %s", request.url.path, exc)
    error_detail = str(exc) if settings.ENVIRONMENT.lower() == "development" else "Internal server error"
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": error_detail, "path": str(request.url.path)},
    )


@app.get("/", tags=["Health & Status"])
def root():
    dist_index = settings.FRONTEND_DIST / "index.html"
    if dist_index.exists():
        return FileResponse(dist_index)
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "OPERATIONAL",
        "documentation": "/docs" if docs_url else "Disabled in production",
        "synthetic_mode": settings.SYNTHETIC_MODE,
        "disclaimer": "AI-assisted mining decision support platform for SIH 2026 PS 26009.",
    }


@app.get("/api/health", tags=["Health & Status"])
def health_check():
    status = runtime_status()
    return {
        **status,
        "models": {
            "forecasting": "LightGBM Quantile (P10, P50, P90)",
            "prospectivity": "XGBoost (Spatial Block CV)",
            "xai": "SHAP TreeExplainer",
            "optimization": "PuLP MILP Solver",
        },
    }


def _mount_frontend() -> None:
    dist = settings.FRONTEND_DIST.resolve()
    assets = dist / "assets"
    if assets.exists():
        app.mount("/assets", StaticFiles(directory=str(assets)), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_spa(full_path: str):
        # Enforce strict path traversal prevention:
        # candidate must resolve to a path strictly within the dist directory
        try:
            candidate = (dist / full_path).resolve()
            if candidate.is_file() and candidate.is_relative_to(dist):
                return FileResponse(candidate)
        except (ValueError, RuntimeError):
            pass

        index = dist / "index.html"
        if index.exists():
            return FileResponse(index)
        return JSONResponse({"detail": "Frontend build not found. Run npm run build in frontend/."}, status_code=404)


_mount_frontend()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host=settings.HOST, port=settings.PORT, reload=False)
