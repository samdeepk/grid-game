# Cloud Run Deployment (Backend)

This guide explains how to build the FastAPI backend into a container image and deploy it to Google Cloud Run.

## 1. Prerequisites

- Google Cloud project with billing enabled.
- `gcloud` CLI ≥ 460 installed locally.
- Artifact Registry (or Container Registry) API enabled.
- Cloud Run API enabled.
- Service account with `roles/run.admin`, `roles/artifactregistry.writer`, and `roles/iam.serviceAccountUser` (or equivalent permissions).
- A PostgreSQL database reachable from Cloud Run. Set the connection string as the `DIRECT_URL` env var (Cloud SQL, Supabase, etc).

Authenticate once:

```bash
gcloud auth login
gcloud config set project <PROJECT_ID>
```

## 2. Build & Push the Image

From the repository root (the backend directory is used as the build context):

```bash
gcloud builds submit server/py3 \
  --tag us-central1-docker.pkg.dev/<PROJECT_ID>/grid-game/grid-game-backend:$(git rev-parse --short HEAD)
```

Update the region/repo path if you store images elsewhere. Artifact Registry repos must exist before running the command (e.g. `gcloud artifacts repositories create grid-game --location=us-central1 --repository-format=DOCKER`).

## 3. Deploy to Cloud Run

Deploy the new image and configure environment variables:

```bash
gcloud run deploy grid-game-backend \
  --image us-central1-docker.pkg.dev/<PROJECT_ID>/grid-game/grid-game-backend:$(git rev-parse --short HEAD) \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --set-env-vars "DIRECT_URL=postgresql+asyncpg://<user>:<pass>@<host>:<port>/<db>"
```

Replace `DIRECT_URL` with the production connection string. If the URL contains special characters, URL-encode them before storing in Cloud Run. For sensitive values, prefer Secret Manager:

```bash
gcloud run services update grid-game-backend \
  --region=us-central1 \
  --update-secrets DIRECT_URL=projects/<PROJECT_ID>/secrets/grid-game-db-url:latest
```

> ℹ️ The container entrypoint (`server/py3/entrypoint.sh`) persists the runtime `DIRECT_URL` (and `DATABASE_URL` fallback) into `/app/.env`, so `load_dotenv()` keeps working without checking real secrets into Git. Just be sure `DIRECT_URL` is provided via Cloud Run env vars or Secret Manager.

## 4. Health Check

Once deployed, verify:

```bash
SERVICE_URL=$(gcloud run services describe grid-game-backend --region=us-central1 --format='value(status.url)')
curl "$SERVICE_URL/"
```

You should receive the JSON response defined in `main.py`.

## 5. Troubleshooting

- **Database errors**: Confirm the Cloud Run service has network access to the database (VPC connector / public IP allowlist). Verify `DIRECT_URL`.
- **Cold start latency**: Consider minimum instances `--min-instances=1`.
- **Long migrations**: Use Cloud Build step or run Alembic migrations separately before deploying.

## 6. Local Docker Test

Before pushing, test locally:

```bash
cd server/py3
docker build -t grid-game-backend .
docker run --rm -p 8080:8080 \
  -e DIRECT_URL=postgresql+asyncpg://... \
  grid-game-backend
```

Visit `http://localhost:8080` to ensure the API boots with the Dockerized environment.

## 7. GitHub Actions (CI/CD)

A workflow at `.github/workflows/backend-cloud-run.yml` automates container builds and deployments:

1. Triggers on pushes to `main` that touch backend/Docker assets, or via manual `workflow_dispatch`.
2. Authenticates to Google Cloud using the `GCP_SA_KEY` JSON secret (workload identity can replace this later).
3. Runs `gcloud builds submit` with `server/py3/Dockerfile`, tagging the image as `REGION-docker.pkg.dev/PROJECT/REPOSITORY/grid-game-backend:<commit-sha>`.
4. Deploys the freshly built image to Cloud Run with `gcloud run deploy`, wiring the `DIRECT_URL` env var from repo secrets.

### Required GitHub Secrets

- `GCP_PROJECT_ID`
- `GCP_REGION`
- `CLOUD_RUN_SERVICE` (e.g. `grid-game-backend`)
- `ARTIFACT_REPOSITORY` (Artifact Registry repo name, e.g. `grid-game`)
- `GCP_SA_KEY` (JSON for a service account with Cloud Build + Artifact Registry + Cloud Run perms)
- `DIRECT_URL` (database connection string or replace with Secret Manager flags)

Update the workflow if you prefer Secret Manager bindings (`--set-secrets`) or workload identity federation.

