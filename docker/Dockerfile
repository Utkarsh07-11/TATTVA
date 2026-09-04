# Multi-stage Dockerfile for SIH 2026 PS 26009 Platform
FROM python:3.11-slim as backend

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt httpx

COPY config/ config/
COPY src/ src/
COPY scripts/ scripts/
COPY data/ data/

# Pre-train and populate models
RUN python scripts/train_pipeline.py

EXPOSE 8000

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
