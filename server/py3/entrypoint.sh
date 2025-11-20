#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="/app/.env"

mkdir -p "$(dirname "${ENV_FILE}")"


echo "**************"
echo "**************"
echo "**************"
echo "DIRECT_URL: ${DIRECT_URL}"
# echo "DATABASE_URL : ${DATABASE_URL}"

# Determine values so .env always has what backend expects
direct_value="${DIRECT_URL:-}"
# database_value="${DATABASE_URL:-${direct_value}}"

# Write secrets to .env so python-dotenv can pick them up
{
  if [[ -n "${direct_value}" ]]; then
    echo "DIRECT_URL=${direct_value}"
  fi
  # if [[ -n "${database_value}" ]]; then
  #   echo "DATABASE_URL=${database_value}"
  # fi
} > "${ENV_FILE}"

exec "$@"

