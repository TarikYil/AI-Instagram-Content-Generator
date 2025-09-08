# Service Upload Dockerfile
FROM python:3.11-slim

# Metadata
LABEL maintainer="AI Instagram Content Generator"
LABEL service="service_upload"
LABEL version="1.0.0"
LABEL description="Oyun içerik yükleme mikroservisi"

# Çalışma dizini
WORKDIR /app

# Sistem paketlerini güncelle ve gerekli paketleri yükle
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python bağımlılıkları için requirements.txt oluştur
COPY requirements.txt .

# Python paketlerini yükle
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Uygulama kodlarını kopyala
COPY . .

# Gerekli dizinleri oluştur
RUN mkdir -p /app/temp /app/logs

# Çalışma izinleri
RUN chmod +x /app/main.py

# Port açık
EXPOSE 8001

# Environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=8001
ENV SERVICE_NAME=service_upload
ENV SERVICE_VERSION=1.0.0

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Uygulama kullanıcısı oluştur (güvenlik için)
RUN useradd -m -u 1001 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Başlangıç komutu
CMD ["python", "main.py"]
