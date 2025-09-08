# Base image
FROM python:3.10-slim

# Çalışma dizini
WORKDIR /app

# Sistem bağımlılıkları (opencv için gerekli kütüphaneler)
RUN apt-get update && apt-get install -y \
    libgl1 libglib2.0-0 ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Requirements yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Proje dosyaları
COPY . .

# FastAPI server çalıştır
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
