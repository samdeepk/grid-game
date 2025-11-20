#!/bin/sh
set -eu

ENV_FILE="/app/.env"

mkdir -p "$(dirname "${ENV_FILE}")"

echo "**************"
echo "**************"
echo "**************"
echo "NEXT_PUBLIC_API_BASE_URL: ${NEXT_PUBLIC_API_BASE_URL:-}"

# Determine values so .env always has what frontend expects
api_base_url="${NEXT_PUBLIC_API_BASE_URL:-}"

# Write environment variables to .env file
{
  if [ -n "${api_base_url}" ]; then
    echo "NEXT_PUBLIC_API_BASE_URL=${api_base_url}"
  fi
} > "${ENV_FILE}"

echo "Created .env file with:"
cat "${ENV_FILE}"

exec "$@"

