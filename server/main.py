"""
ReLife AI — FastAPI Main Application
Full 7-feature platform for Amazon Hackathon
Deployable on AWS EC2 (t2.micro Free Tier)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from routers import (lifecycle, vision, recommendations,
                     credits, p2p, cart, dashboard, notifications)

app = FastAPI(
    title="ReLife AI API",
    description="Intelligent Second-Life Commerce Platform — Amazon Hackathon",
    version="2.0.0",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all feature routers
for router in [
    lifecycle.router,
    vision.router,
    recommendations.router,
    credits.router,
    p2p.router,
    cart.router,
    dashboard.router,
    notifications.router,
]:
    app.include_router(router)


@app.get("/health")
def health():
    return {
        "status":  "ok",
        "service": "ReLife AI",
        "version": "2.0.0",
        "env":     settings.APP_ENV,
        "features": [
            "AI Lifecycle Engine",
            "Vision Quality Grading",
            "Personalized Recommendations",
            "Green Credits",
            "P2P Marketplace",
            "Return Prevention",
            "Sustainability Dashboard",
        ],
    }


@app.get("/")
def root():
    return {"message": "Welcome to ReLife AI 🌿 — Visit /docs for the API reference"}


# ============================================================
# Production entrypoint (for EC2 / Docker)
# ============================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=not settings.is_production,
    )
