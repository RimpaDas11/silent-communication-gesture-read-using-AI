# AI-Driven Development Plan: Gesture-to-Text System

## Overview

Build a **Gesture-to-Text Translation System** using a **Monorepo Architecture** with a strict phased roadmap.

### Core Goals
1. **Backend First**
2. **Web Frontend Second**
3. **Integration Third**
4. **Mobile Frontend Later**

---

## Global AI Context (System Prompt)

**Role:** Expert Full-Stack Machine Learning Engineer  
**Task:** Build a Gesture-to-Text translation platform.

### Primary Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+, FastAPI, Uvicorn |
| CV / ML | OpenCV, NumPy |
| Validation | Pydantic |
| Web Frontend | React + TypeScript |
| HTTP Client | Axios |
| Mobile (Future) | React Native + TypeScript |

### Development Rules

- Write modular and reusable code
- Use strict typing everywhere
- Follow API contracts exactly
- Separate backend routes using `APIRouter`
- Treat each folder as an independent workspace

---

# Monorepo File Structure

```text
/
├── README.md
├── .gitignore
│
├── backend/
│   ├── README.md
│   ├── .gitignore
│   ├── main.py
│   ├── requirements.txt
│   ├── api/
│   │   └── routes/
│   │       ├── predict.py
│   │       └── live.py
│   ├── schemas/
│   │   └── prediction.py
│   └── services/
│       └── model_handler.py
│
├── web-frontend/
│   ├── README.md
│   ├── .gitignore
│   ├── package.json
│   ├── tsconfig.json
│   └── src/
│       ├── api/
│       │   └── axios.ts
│       ├── components/
│       │   ├── ImageUpload.tsx
│       │   ├── VideoUpload.tsx
│       │   └── LiveWebcam.tsx
│       └── App.tsx
│
└── mobile-frontend/
    └── future/
```

---

# API Contracts

## 1. Image / Video POST Response

```json
{
  "status": "success | error",
  "filename": "string",
  "prediction": "string",
  "error_message": null
}
```

## TypeScript Interface

```ts
export interface PredictionResponse {
  status: 'success' | 'error';
  filename: string;
  prediction: string;
  error_message: string | null;
}
```

---

## 2. WebSocket Protocol

### Client → Server
- Raw Base64 JPEG frame

### Server → Client
- Plain text prediction

Example:

```text
Thumbs Up
```

---

# Development Phases

# Phase 1 — Backend Setup

## Task 1.1 Dependencies

Create:

- `.gitignore`
- `README.md`
- `requirements.txt`

Include:

```txt
fastapi
uvicorn
python-multipart
opencv-python-headless
pydantic
numpy
```

---

## Task 1.2 Schema

Create:

```text
backend/schemas/prediction.py
```

Model:

```python
PredictionResponse
```

Fields:

- status
- filename
- prediction
- error_message

---

## Task 1.3 Model Handler

Create:

```text
backend/services/model_handler.py
```

Class:

```python
GestureCNN
```

Methods:

- `__init__()`
- `predict_frame(frame_array)`

Return mock values:

- Hello
- Thumbs Up

Global instance:

```python
cnn_service
```

---

# Phase 2 — FastAPI Routes

## Task 2.1 Prediction Routes

Create:

```text
backend/api/routes/predict.py
```

Router:

```python
APIRouter(prefix="/api/predict")
```

Endpoints:

### POST /image
- Upload image
- Decode via OpenCV
- Predict result

### POST /video
- Save temp file
- Process every 10th frame
- Aggregate predictions

---

## Task 2.2 WebSocket Route

Create:

```text
backend/api/routes/live.py
```

Endpoint:

```text
/ws/live
```

Flow:

1. Accept socket
2. Receive frame
3. Predict gesture
4. Send text response

---

## Task 2.3 Main App

Create:

```text
backend/main.py
```

Include:

- FastAPI instance
- CORS enabled
- Include routers

---

# Phase 3 — React Frontend

## Task 3.1 Axios Wrapper

Create:

```text
web-frontend/src/api/axios.ts
```

Functions:

```ts
uploadImage(file)
uploadVideo(file)
```

Base URL:

```text
http://localhost:8000
```

---

## Task 3.2 Upload Components

Create:

```text
ImageUpload.tsx
VideoUpload.tsx
```

Features:

- File input
- Submit button
- Loading state
- Show prediction

---

## Task 3.3 Live Webcam

Create:

```text
LiveWebcam.tsx
```

Use:

- WebSocket
- getUserMedia()
- hidden canvas
- send frame every 200ms

Cleanup on unmount.

---

# Phase 4 — Integration Testing

Run simultaneously:

## Backend

```bash
uvicorn main:app --reload
```

## Frontend

```bash
npm run dev
```

Test:

- Image Upload
- Video Upload
- Webcam Stream
- CORS
- JSON schema consistency

---

# Phase 5 — Future Scope

## Mobile Frontend

Use:

- React Native
- Vision Camera

## Production ML Upgrade

Replace mock model with:

- PyTorch
- TensorFlow

---

# Recommended Workflow

1. Complete backend first
2. Test APIs with Postman
3. Build frontend UI
4. Integrate WebSocket stream
5. Add real ML model later

---

# Final Note

This roadmap is ideal for:

- Final year project
- AI portfolio project
- Startup MVP
- Computer Vision learning

