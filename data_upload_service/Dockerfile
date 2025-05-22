FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    libffi-dev \
    libssl-dev \
    libpq-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose internal port
EXPOSE 8000

# Start the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

