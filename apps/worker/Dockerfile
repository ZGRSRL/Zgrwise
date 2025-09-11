FROM python:3.11-slim

# Set working directory
WORKDIR /worker

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Configure Poetry
RUN poetry config virtualenvs.create false

# Copy Poetry files
COPY pyproject.toml ./

# Install dependencies
RUN poetry install --only=main --no-root

# Copy application code
COPY . .

# Run the worker
CMD ["python", "-m", "worker.main"]