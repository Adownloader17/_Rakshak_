
# rakshak-ui (React + Vite)

This folder contains the lightweight React frontend demo for Rakshak. It is a Vite app that calls the local FastAPI backend (`http://127.0.0.1:8000` by default) and provides two tabs: XSS payload testing and URL phishing checks.

## Quick start

From the `rakshak-ui/` directory:

```powershell
cd rakshak-ui
npm install
npm run dev
```

Open the dev server URL (usually `http://localhost:5173`). The UI reads the API base URL from `src/config.js` (default: `http://127.0.0.1:8000`).

## Build / Preview

```powershell
npm run build
npm run preview
```

## Tailwind CSS

This project may use Tailwind classes. To enable Tailwind in a Vite project, install and initialize it (you may have already done this):

```powershell
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

Then add the `./index.css` import and configure `tailwind.config.js` content paths to include `src/**/*`.

## Configuration

- `src/config.js` exposes `API_BASE` — change this if your API runs elsewhere.

## Lint & Common issues

- ESLint can flag unused variables. A recent change replaced `catch (e)` with `catch { ... }` in `src/App.jsx` to avoid an unused `e` warning.

## Notes

- Ensure the backend API is running (`uvicorn src.api.app:app --reload --port 8000`) when testing the UI locally.
- CORS is enabled broadly in the example `app.py` to simplify local development; tighten it for production.
