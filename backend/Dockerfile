# backend/Dockerfile
FROM python:3.12-slim-bookworm

# Set environment variables for non-interactive installs and unbuffered Python output
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=2.3.4 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false

# Add Poetry to PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

# Install system dependencies for wkhtmltopdf and WeasyPrint
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wkhtmltopdf \
    weasyprint \
    build-essential \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Set working directory
WORKDIR /app

# Copy dependency files first (to leverage Docker layer caching)
COPY pyproject.toml poetry.lock* ./

# Install Python dependencies
RUN poetry install --no-root

# Copy the rest of the application
COPY . .

# Expose the API port
EXPOSE 8000

# Run the application securely via uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000" , "--proxy-headers", "--forwarded-allow-ips", "*" ]