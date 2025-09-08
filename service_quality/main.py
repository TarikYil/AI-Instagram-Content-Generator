from fastapi import FastAPI
from routes import quality_routes
import uvicorn
import logging

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(
    title="Service Quality - AI Image Quality Assessment",
    description="Text-to-image quality metrikleri ve görsel kalite değerlendirmesi",
    version="1.0.0",
    docs_url="/docs",
)

# Route include
app.include_router(quality_routes.router)

@app.get("/")
def root():
    return {"message": "Quality Assessment Service is running", "service": "service_quality"}

@app.get("/health")
async def health():
    return {"status": "ok", "service": "service_quality"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8005,  # Quality servisi için port 8005
        reload=True
    )
