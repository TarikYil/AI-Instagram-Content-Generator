from fastapi import FastAPI
from routes.upload_routes import router as upload_router
import uvicorn

app = FastAPI(
    title="Service Upload - Oyun İçerik Yükleme Servisi",
    description="Oyun videosu, görseller, ASO keyword ve açıklamaları Google Drive'a yükler",
    version="1.0.0",
    docs_url="/docs",
)

# Route ekleme
app.include_router(upload_router)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "service_upload"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",              # main.py içindeki "app" objesini çalıştır
        host="0.0.0.0",          # tüm IP'lerden erişilebilir olsun
        port=8001,               # portu 8001 seçtik (istersen değiştirebilirsin)
        reload=True              # kod değişikliklerinde otomatik reload (dev için)
    )
