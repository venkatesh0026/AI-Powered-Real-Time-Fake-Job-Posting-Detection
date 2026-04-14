# Fake Job Post Detection System

A full-stack application to detect fraudulent job postings using a BERT-based deep learning model.

## Project Structure

```
fake_job_detection/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── middleware/      # Auth middleware
│   │   ├── routes/          # API routes (predict, health)
│   │   ├── services/        # Model service
│   │   └── utils/           # Config utilities
│   ├── ml/
│   │   ├── bert_model_output/  # Trained BERT model
│   │   ├── code/            # Training notebooks/scripts
│   │   └── dataset/         # Job postings dataset
│   ├── main.py              # FastAPI app entry
│   ├── requirements.txt     # Python dependencies
│   └── .env.template        # Environment template
├── frontend/                # React frontend
│   ├── src/
│   │   ├── components/      # Reusable components
│   │   ├── context/         # Auth context
│   │   ├── lib/             # Supabase client
│   │   ├── pages/           # App pages
│   │   └── App.jsx          # Main app
│   ├── package.json         # Node dependencies
│   └── vite.config.js       # Vite config
├── docs/                    # Documentation
│   └── RETRAINING_INSTRUCTIONS.md
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## Architecture

- **Frontend**: React (Vite) + Supabase Auth
- **Backend API**: FastAPI (PyTorch + Hugging Face Transformers for inference)
- **Auth / DB**: Supabase (Auth only; optional PostgreSQL)

The frontend runs on port 5173 and proxies `/api` to the backend. The backend serves the prediction API and interactive docs.

## Prerequisites

- Node.js (v16+)
- Python (v3.8+)
- Supabase project (URL and Anon Key for the frontend)

## Setup Instructions

### 1. Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment (or use the project root `.venv`):
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   - Create a `.env` file in `backend/` with:
     - `SUPABASE_URL` – your Supabase project URL
     - `SUPABASE_KEY` – Supabase anon (or service) key for token verification
     - `SECRET_KEY` – app secret (e.g. for sessions)
   - **Model path**: The app uses the BERT model in `backend/ml/bert_model_output/` by default. You can override with `MODEL_PATH` (full or relative path to that directory). Do not point to a `.pt` file; the loader expects the directory containing `config.json`, `model.safetensors`, and tokenizer files.

5. Run the API server (FastAPI with auto-reload):
   ```bash
      & ".\.venv\Scripts\Activate.ps1"
   uvicorn backend.main:app --reload
   uvicorn main:app --reload --port 5000
   ```
   - API base: `http://localhost:5000`
   - **API docs (Swagger)**: `http://localhost:5000/docs`
   - ReDoc: `http://localhost:5000/redoc`

   Alternatively, you can run the Flask app (no built-in API docs):
   ```bash
   python run.py
   ```
   This also serves the API at `http://localhost:5000`.

### 2. Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Configure environment variables:
   - Create a `.env` file in `frontend/` with:
     ```
     VITE_SUPABASE_URL=your_supabase_url
     VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
     ```

4. Start the development server:
   ```bash
   npm run dev
   ```
   The app will be at `http://localhost:5173`. Requests to `/api/*` are proxied to `http://localhost:5000`.

## API Endpoints

- **`GET /`** – API status and link to docs.
- **`GET /health`** – Health check (returns `{"status": "healthy"}`).
- **`POST /api/predict`** – Fake job prediction (requires `Authorization: Bearer <token>`).
  - **Content-Type**: `application/json`
  - **Body**:
    ```json
    {
      "title": "Job title",
      "company": "Company name",
      "description": "Full job description",
      "requirements": "Optional",
      "benefits": "Optional"
    }
    ```
  - **Response**: `label` (Genuine/Fake), `confidence`, `probability_fraud`, `details`, and optionally `is_mock` (true when the model is not loaded).

## Model Information

- **Location**: `backend/ml/bert_model_output/`
- **Contents**: BERT model and tokenizer (e.g. `config.json`, `model.safetensors`, `tokenizer.json`, `tokenizer_config.json`). The path is resolved from the backend package root so it works whether you run the server from the project root or the `backend` directory.
- **Retraining**: See `docs/RETRAINING_INSTRUCTIONS.md` for Colab-based retraining, threshold tuning, and replacing the model in this directory.
- **Inference**: `model_service.py` loads the model at startup; if the path is missing or invalid, the API returns mock “Genuine” results with `is_mock: true`.

## Quick Start (Backend + API Docs)

From the project root:

```bash
# Backend
cd backend
uvicorn main:app --reload --port 5000
```

Then open **http://localhost:5000/docs** to try the API with Swagger UI.
