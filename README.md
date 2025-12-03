# Rakshak

Rakshak is a small security-focused project that provides simple feature extraction and ML models for detecting web attacks (phishing URLs and XSS payloads). It contains backend API code, model training scripts, example datasets, and a lightweight React frontend demo.

This README covers the repository overview, setup for local development (backend + frontend), and quick commands to run the API and UI.

## Quick links
- Backend code: `src/`
- Frontend UI: `rakshak-ui/`
- Data: `data/raw/` and `data/processed/`
- Models: `src/models/` (trained model artifacts: `phishing_model.joblib`, `xss_model.joblib`)

## Repository layout

- `data/raw/` – raw CSV files (example: `malicious_phish.csv`).
- `data/processed/` – processed datasets created by experiments.
- `notebooks/` – Jupyter notebooks used during development.
- `src/` – backend code (FastAPI app, feature extractors, training scripts, model artifacts).
  - `src/api/app.py` – FastAPI application exposing `/predict/xss` and `/predict/url` endpoints.
  - `src/features/` – feature extraction helpers: `url_features.py`, `xss_features.py`.
  - `src/models/` – training scripts and saved models.
- `rakshak-ui/` – React + Vite frontend demo that calls the local API.

## Setup (backend)

1. Create and activate a virtual environment (recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install Python dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

3. Run the API locally (from repository root):

```powershell
.\.venv\Scripts\python.exe -m uvicorn src.api.app:app --reload --host 127.0.0.1 --port 8000
```

API endpoints:
- `GET /health` – health check
- `POST /predict/url` – body `{ "url": "..." }` → returns `{ label, score, reasons }`
- `POST /predict/xss` – body `{ "payload": "..." }` → returns `{ label, score, reasons }`

## Training models

- Phishing training script: `python src/models/train_phishing.py` (saves model to `src/models/phishing_model.joblib`).
- XSS training script: `python src/models/train_xss.py` (saves model to `src/models/xss_model.joblib`).

Ensure `data/raw/` contains the expected CSV files before running training.

## Frontend (rakshak-ui)

The `rakshak-ui` folder contains a lightweight React + Vite demo that calls the local FastAPI backend (`http://127.0.0.1:8000` by default). The UI provides two tabs: XSS payload testing and URL phishing checks.

### Quick start (development)

From the repository root or within `rakshak-ui/`:

```powershell
cd rakshak-ui
npm install
npm run dev
```

Open the dev server URL (usually `http://localhost:5173`). The UI reads the API base URL from `src/config.js` (default: `http://127.0.0.1:8000`).

### Build / Preview

```powershell
npm run build
npm run preview
```

### Tailwind CSS

This project may use Tailwind classes. To enable Tailwind in a Vite project if needed:

```powershell
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

Then ensure `index.css` imports Tailwind and `tailwind.config.js` content paths include `src/**/*`.

### Configuration

- `src/config.js` exposes `API_BASE` — change this if your API runs elsewhere.

### Lint & Common issues

- ESLint can flag unused variables. A recent change replaced `catch (e)` with `catch { ... }` in `src/App.jsx` to avoid an unused `e` warning.

### Notes

- Ensure the backend API is running (`uvicorn src.api.app:app --reload --port 8000`) when testing the UI locally.
- CORS is enabled broadly in the example `app.py` to simplify local development; tighten it for production.

## Workspace analysis (short)

- Backend: `src/api/app.py` (FastAPI), `src/features/` (feature extractors), `src/models/` (training + saved models).
- Frontend: `rakshak-ui/src/` contains `App.jsx` (UI), `main.jsx`, and `config.js` for API base URL.
- Data: `data/raw/` contains CSVs used for training. Confirm these files exist before training.

Recommended next actions:
- Add `__init__.py` files to `src/`, `src/features/`, and `src/models/` if you prefer package-style imports (or run Python with `PYTHONPATH` set). I can add these automatically.
- Add or update `src/features/url_features.py` and `src/features/xss_features.py` if feature extraction code is missing or incomplete.
- Pin exact dependency versions in `requirements.txt` for CI reproducibility.
- Add simple scripts in `scripts/` to run training + serve the API for reproducible workflows.

## Troubleshooting

- If you see `ModuleNotFoundError: No module named 'src.features.url_features'` when running Python, either add package markers (`__init__.py`) or run with `PYTHONPATH` set to the project root:

```powershell
$env:PYTHONPATH='C:\path\to\Rakshak\rakshak'; .\.venv\Scripts\python.exe src\models\train_phishing.py
```

- After editing package files, reload VS Code (Developer: Reload Window) so language servers rescan the workspace.




