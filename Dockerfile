FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Pull latest from git to ensure we have latest code
RUN git pull origin main || echo "Git pull skipped (OK if no repo)"

# Verify database file exists
RUN ls -lh database.json && wc -l database.json

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080')" || exit 1

# Run Flask app
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8080", "webhook_server:app"]
