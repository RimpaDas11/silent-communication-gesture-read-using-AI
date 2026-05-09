"""
Pydantic schemas for Gesture-to-Text prediction responses.
Matches the API contract defined in the project specification.
"""

from __future__ import annotations

from typing import Literal
from pydantic import BaseModel


class PredictionResponse(BaseModel):
    """Standard response model for all gesture prediction endpoints."""

    status: Literal["success", "error"]
    filename: str
    prediction: str
    error_message: str | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "success",
                    "filename": "gesture.jpg",
                    "prediction": "Thumbs Up",
                    "error_message": None,
                }
            ]
        }
    }
