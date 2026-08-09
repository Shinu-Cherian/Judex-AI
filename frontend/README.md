# Judex AI — Frontend

React 19 + Vite frontend for Judex AI. See the [root README](../README.md)
for the full project overview, architecture, and setup instructions.

## Local development

```bash
npm install
npm run dev
```

Runs on `http://localhost:5173` and proxies `/api` requests to the backend
at `http://localhost:7771` (configured in `vite.config.js`).

## Build

```bash
npm run build
```

Outputs to `dist/`, which the FastAPI backend serves directly in production
(see `backend/main.py`).
