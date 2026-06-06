# Dockerfile.backend
FROM python:3.11-slim

# Install system dependencies for PyMuPDF (fitz) and Tesseract OCR
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-hin \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend files
COPY app.py .
COPY bns_mapping.py .

EXPOSE 5050

# Run Flask backend with Gunicorn in production
CMD ["gunicorn", "--bind", "0.0.0.0:5050", "app:app", "--workers", "1", "--threads", "2", "--timeout", "120"]
