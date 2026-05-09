# Backend — Gesture-to-Text API

FastAPI backend powering the gesture recognition engine.

## Setup (UV)

```bash
# Create virtual environment
uv venv

# Activate it
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt
```

## Run Dev Server

```bash
uvicorn main:app --reload
```

Server runs at: http://localhost:8000

## API Docs

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints

| Method | Path | Description |
|---|---|---|
| POST | /api/predict/image | Upload image for prediction |
| POST | /api/predict/video | Upload video for prediction |
| WS | /ws/live | Live webcam stream |

## Project Structure

```
backend/
├── main.py               # FastAPI app entry point
├── requirements.txt      # Python dependencies
├── api/
│   └── routes/
│       ├── predict.py    # Image & video upload endpoints
│       └── live.py       # WebSocket live stream
├── schemas/
│   └── prediction.py     # Pydantic response models
└── services/
    └── model_handler.py  # GestureCNN mock service
```
