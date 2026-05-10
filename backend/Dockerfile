# ─── Build stage ──────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system dependencies for pyodbc / Pillow
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ─── Runtime stage ─────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Runtime deps only
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy app source
COPY . .

# Create uploads directory for local storage fallback
RUN mkdir -p uploads/photos uploads/thumbnails

# Non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
