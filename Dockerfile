# ============================================
# PhongTro.vn Production Dockerfile
# Multi-stage build for security & efficiency
# ============================================

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    unixodbc \
    unixodbc-dev \
    curl \
    gnupg \
    apt-transport-https \
    && rm -rf /var/lib/apt/lists/*

# Install Microsoft ODBC Driver 18 for SQL Server
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# ============================================
# Stage 2: Production
# ============================================
FROM python:3.11-slim as production

# Security: Create non-root user
RUN groupadd -r phongtro && useradd -r -g phongtro phongtro

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    unixodbc \
    && rm -rf /var/lib/apt/lists/*

# Install Microsoft ODBC Driver 18
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY --chown=phongtro:phongtro . .

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs /app/media /app/staticfiles && \
    chown -R phongtro:phongtro /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production

# Switch to non-root user (Security best practice)
USER phongtro

# Collect static files (don't run migrations in Dockerfile!)
RUN python manage.py collectstatic --noinput || true

# Expose port
EXPOSE 8000

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Run with gunicorn
CMD ["gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "--threads", "2", \
     "--worker-class", "gthread", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--capture-output", \
     "--timeout", "120"]