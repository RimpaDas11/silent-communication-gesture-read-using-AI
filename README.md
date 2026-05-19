# Gesture-to-Text Translation System

A real-time gesture recognition platform that translates hand gestures into text using computer vision and machine learning.

## Monorepo Structure

```
/
├── backend/          # Python FastAPI backend (CV/ML engine)
├── web-frontend/     # React + TypeScript web app
└── mobile-frontend/  # React Native app (future scope)
```

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+, FastAPI, Uvicorn |
| CV / ML | OpenCV, NumPy |
| Validation | Pydantic |
| Web Frontend | React + TypeScript |
| HTTP Client | Axios |

## Quick Start

### Backend
```bash
cd backend
uv venv
uv pip install -r requirements.txt
uvicorn main:app --reload
```

### Web Frontend
```bash
cd web-frontend
npm install
npm run dev
```

## Development Phases

| Phase | Description | Status |
|---|---|---|
| Phase 1 | Backend Setup (schemas, model handler) | ✅ Done |
| Phase 2 | FastAPI Routes (predict + websocket) | ✅ Done |
| Phase 3 | React Frontend | ✅ Done|
| Phase 4 | Integration Testing | ✅ Done |
| Phase 5 | Mobile + Real ML Model | 🔜 Future |
