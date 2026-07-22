from fastapi import FastAPI

app = FastAPI(
    title="PlacementPilot AI",
    description="AI-powered Placement Readiness & ATS Analysis Platform",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "Welcome to PlacementPilot AI 🚀",
        "status": "Backend is running successfully!"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }