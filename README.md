# grid-game

Monorepo containing the FastAPI backend (`server/py3`) and the React frontend (`webapp/grid-react`).

## Backend Deployment

The backend can be containerized and deployed to Google Cloud Run manually or via GitHub Actions. See `server/py3/CLOUD_RUN.md` for:

- Dockerfile details and local testing instructions
- `gcloud` build/push/deploy flow (`gcloud builds submit . --file server/py3/Dockerfile ...`)
- CI/CD workflow description (`.github/workflows/backend-cloud-run.yml`) and required secrets (workflow injects the `DIRECT_URL` secret used by `server/py3/entrypoint.sh` to hydrate `/app/.env`)
- React frontend build is baked into the backend image—`pnpm run build:static` runs inside the Docker multi-stage build and the generated files are served from FastAPI (`/`), while `/healthz` exposes a JSON health probe.
