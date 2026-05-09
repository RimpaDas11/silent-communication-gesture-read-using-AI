"""
main.py — FastAPI application entry point.

Run with:
    uvicorn main:app --reload
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import predict, live

# ---------------------------------------------------------------------------
# Application instance
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Gesture-to-Text API",
    description=(
        "Real-time hand gesture recognition API.\n\n"
        "Supports image upload, video upload, and live WebSocket streaming."
    ),
    version="0.1.0",
)

# ---------------------------------------------------------------------------
# CORS — allow the React dev server (and any origin in dev)
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",   # React (CRA default)
        "http://localhost:5173",   # Vite default
        "http://localhost:5174",   # Vite alternate port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(predict.router)
app.include_router(live.router)

# ---------------------------------------------------------------------------
# Health-check root
# ---------------------------------------------------------------------------

@app.get("/", tags=["health"])
async def root() -> dict[str, str]:
    """Simple health-check endpoint."""
    return {"status": "ok", "message": "Gesture-to-Text API is running 🚀"}
