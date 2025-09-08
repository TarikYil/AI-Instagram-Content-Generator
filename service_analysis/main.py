from fastapi import FastAPI
from routes import analyses_route
import uvicorn

app = FastAPI(
    title="Service Analysis - İçerik Analiz Servisi",
    description="Google Drive'dan dosyaları çekip AI ile analiz eder",
    version="1.0.0",
    docs_url="/docs",
)

# Route include
app.include_router(analyses_route.router)

@app.get("/")
def root():
    return {"message": "Content Analysis Service is running", "service": "service_analysis"}

@app.get("/health")
async def health():
    return {"status": "ok", "service": "service_analysis"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",              # main.py içindeki "app" objesini çalıştır
        host="0.0.0.0",          # tüm IP'lerden erişilebilir olsun
        port=8003,               # portu 8003 seçtik
        reload=True              # kod değişikliklerinde otomatik reload (dev için)
    )