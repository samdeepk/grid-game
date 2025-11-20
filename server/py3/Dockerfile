# syntax=docker/dockerfile:1


FROM python:3.11-slim AS base
ARG DIRECT_URL

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    PORT=8080

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm -f /tmp/requirements.txt

COPY . /app
RUN chmod +x /app/entrypoint.sh


ENV DIRECT_URL=${DIRECT_URL}
RUN echo "DIRECT_URL $DIRECT_URL"
# RUN ["echo", "DATABASE_URL :" , $DATABASE_URL]

ENV PYTHONPATH=/app

EXPOSE 8080

ENTRYPOINT ["./entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]

