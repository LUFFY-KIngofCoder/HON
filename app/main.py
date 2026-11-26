from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import engine, Base
from app.models import (
    ChicagoCrime, IUCRCode, CityCommunity,
    DistrictPSInfo, PoliceBeatInfo, WardOffice,
)
from app.routers.analytics import router as analytics_router
from app.routers.crud import router as crud_router

# ── App Metadata ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="Chicago Crime Analytics API",
    description=(
        "REST API serving the Chicago Crime Analytics dashboard and all 6 "
        "relational database tables (chicago_crime, iucr_codes, city_community, "
        "district_ps_info, police_beat_info, ward_office) with full CRUD support."
    ),
    version="1.0.0",
)

# ── CORS (allow Streamlit on any local port to call the API) ─────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
)

# ── Register Routers ──────────────────────────────────────────────────────────
app.include_router(analytics_router)
app.include_router(crud_router)


# ── Health Check ─────────────────────────────────────────────────────────────
@app.get("/health", tags=["System"])
def health():
    return {"status": "ok", "database": str(engine.url)}


# ── Root ──────────────────────────────────────────────────────────────────────
@app.get("/", tags=["System"])
def root():
    return {
        "message": "Chicago Crime Analytics API",
        "docs": "/docs",
        "analytics_endpoints": [
            "/api/analytics/kpis",
            "/api/analytics/yearly",
            "/api/analytics/categories",
            "/api/analytics/heatmap",
            "/api/analytics/daily",
            "/api/analytics/communities",
        ],
        "crud_tables": [
            "chicago_crime", "iucr_codes", "city_community",
            "district_ps_info", "police_beat_info", "ward_office",
        ],
    }
