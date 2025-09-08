from fastapi import FastAPI
from routes import generation_routes
import uvicorn
import logging

# Logging seviyesini DEBUG yap
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(
    title="Service Generation - AI İçerik Üretim Servisi",
    description="Trend ve analiz verilerinden AI ile Instagram içeriği üretir",
    version="1.0.0",
    docs_url="/docs",
)

# Route include
app.include_router(generation_routes.router)

@app.get("/")
def root():
    return {"message": "Content Generation Service is running", "service": "service_generation"}

@app.get("/health")
async def health():
    return {"status": "ok", "service": "service_generation"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8004,  # Generation servisi için port 8004
        reload=True,
        log_level="debug"  # Debug logging
    )
