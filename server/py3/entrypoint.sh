#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="/app/.env"

mkdir -p "$(dirname "${ENV_FILE}")"


echo "**************"
echo "**************"
echo "**************"
echo "DIRECT_URL: ${DIRECT_URL}"
echo "CORS_ALLOWED_ORIGINS: ${CORS_ALLOWED_ORIGINS:-}"
# echo "DATABASE_URL : ${DATABASE_URL}"

# Determine values so .env always has what backend expects
direct_value="${DIRECT_URL:-}"
cors_origins="${CORS_ALLOWED_ORIGINS:-}"
# database_value="${DATABASE_URL:-${direct_value}}"

# Write secrets to .env so python-dotenv can pick them up
{
  if [[ -n "${direct_value}" ]]; then
    echo "DIRECT_URL=${direct_value}"
  fi
  if [[ -n "${cors_origins}" ]]; then
    echo "CORS_ALLOWED_ORIGINS=${cors_origins}"
  fi
} > "${ENV_FILE}"

exec "$@"

