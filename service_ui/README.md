# AI Instagram Content Generator - Web UI

Modern Streamlit tabanlı web arayüzü ile 5 mikroservisi orkestre eden AI içerik üretim pipeline'ı.

## 🚀 Özellikler

- **Material Upload**: Video, görsel ve metin yükleme
- **Trend Analysis**: YouTube/Instagram trend analizi
- **Content Analysis**: AI ile materyal analizi (BLIP + ASO)
- **Content Generation**: Stable Diffusion ile görsel üretimi
- **Quality Assessment**: CLIP + Aesthetic scoring
- **Workflow Orchestration**: Otomatik pipeline yönetimi

## 🏗️ Mikroservis Mimarisi

1. **service_upload** (Port 8001): Dosya yükleme
2. **service_analysis** (Port 8003): İçerik analizi
3. **service_trend** (Port 8005): Trend analizi
4. **service_generation** (Port 8004): İçerik üretimi
5. **service_quality** (Port 8006): Kalite değerlendirmesi

## 📦 Kurulum

```bash
# Bağımlılıkları yükle
pip install -r requirements.txt

# UI'yi başlat
streamlit run app.py
```

## 🎯 Kullanım Akışı

1. **Upload**: Materyal yükleme (görsel, video, keywords)
2. **Process**: Trend analizi + Materyal analizi
3. **Generate**: AI ile görsel ve içerik üretimi
4. **Quality**: Kalite değerlendirmesi + Finalizasyon

## 🔧 Gereksinimler

- Python 3.8+
- Tüm mikroservislerin çalışır durumda olması
- Google Drive API credentials (service_analysis için)
- CUDA destekli GPU (opsiyonel, CPU fallback mevcut)

## 📊 Dashboard Özellikleri

- **Real-time Status**: Mikroservis sağlık durumu
- **Workflow Progress**: Adım adım ilerleme takibi
- **Live Logs**: Detaylı işlem logları
- **Preview Area**: Üretilen içeriğin önizlemesi
- **Final Output**: Yayına hazır paket

## 🎨 UI Bileşenleri

- Material uploader
- Step-by-step workflow buttons
- Real-time status logs
- Generated content preview
- Quality metrics dashboard
- Final publish-ready output
