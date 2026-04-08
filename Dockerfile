FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive \
    ACCEPT_EULA=Y

# System dependencies and MS SQL ODBC driver
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    apt-transport-https \
    gnupg \
    bash \
    build-essential \
    unixodbc-dev \
    && mkdir -p /etc/apt/keyrings /etc/apt/sources.list.d \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /etc/apt/keyrings/microsoft.gpg \
    && chmod 644 /etc/apt/keyrings/microsoft.gpg \
    && echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends msodbcsql18 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies (web)
COPY requirements-web.txt ./
RUN pip install -r requirements-web.txt

# Copy application code
COPY . .
# Normalize potential Windows line endings for shell scripts
RUN sed -i 's/\r$//' start.sh

# Ensure startup script is executable
RUN chmod +x start.sh \
    && useradd -m appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 CMD curl -f http://localhost:8080/health || exit 1

ENTRYPOINT ["./start.sh"]
