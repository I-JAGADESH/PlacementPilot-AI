from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database.database import Base, engine

# ============================================================
# DATABASE MODELS
# ============================================================

import app.database.models
import app.training.models
import app.assessment.models
import app.interview.models
import app.ats.models
import app.github.models


# ============================================================
# API ROUTERS
# ============================================================

from app.api.auth import router as auth_router
from app.api.profile import router as profile_router
from app.api.ats import router as ats_router
from app.api.intelligence import router as intelligence_router
from app.api.roadmap import router as roadmap_router
from app.api.interview import router as interview_router
from app.api.readiness import router as readiness_router
from app.api.training import router as training_router
from app.api.assessment import router as assessment_router
from app.github.api import router as github_router


# ============================================================
# APPLICATION LIFESPAN
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Create database tables when the application starts.
    """
    Base.metadata.create_all(bind=engine)
    yield


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "AI-powered Placement Readiness, "
        "ATS Analysis and Personalized "
        "Placement Preparation Platform"
    ),
    version=settings.VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# API ROUTERS
# ============================================================

app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(ats_router)
app.include_router(intelligence_router)
app.include_router(roadmap_router)
app.include_router(interview_router)
app.include_router(readiness_router)
app.include_router(training_router)
app.include_router(assessment_router)
app.include_router(github_router)


# ============================================================
# ROOT
# ============================================================

@app.get(
    "/",
    tags=["Root"],
)
async def root():
    return {
        "application": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "running",
        "documentation": "/api/docs",
    }


# ============================================================
# HEALTH
# ============================================================

@app.get(
    "/api/v1/health",
    tags=["Health"],
)
async def health():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.VERSION,
    }


# ============================================================
# PING
# ============================================================

@app.get(
    "/api/v1/ping",
    tags=["Health"],
)
async def ping():
    return {
        "ping": "pong",
    }
