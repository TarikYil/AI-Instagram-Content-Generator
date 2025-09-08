from fastapi import FastAPI
from routes import analyzes_routes
import uvicorn

app = FastAPI(title="Trend Analysis Service")

app.include_router(analyzes_routes.router)

@app.get("/")
def root():
    return {"message": "Trend Analysis API is running"}

@app.get("/health")
async def health():
    return {"status": "ok", "service": "service_trend"}
if __name__ == "__main__":
    uvicorn.run(
        "main:app",              # main.py içindeki "app" objesini çalıştır
        host="0.0.0.0",          # tüm IP'lerden erişilebilir olsun
        port=8002,               # portu 8001 seçtik (istersen değiştirebilirsin)
        reload=True              # kod değişikliklerinde otomatik reload (dev için)
    )