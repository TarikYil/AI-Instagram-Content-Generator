from fastapi import APIRouter
from modules.trend_agent import TrendAgent
from helpers.utils import get_env

router = APIRouter(prefix="/analyzes", tags=["Analyzes"])

@router.get("/youtube")
def youtube_trends():
    """YouTube trend analysis"""
    try:
        # API key'ini buraya yapıştır (tırnak içinde)
        api_key = "YOUR_YOUTUBE_API_KEY_HERE"  # <-- Buraya API key'ini yapıştır
        
        if api_key == "YOUR_YOUTUBE_API_KEY_HERE" or not api_key:
            # API key yoksa mock data döndür
            mock_trends = ["AI Technology", "Gaming Setup", "Content Creation", "Digital Art"]
            mock_hashtags = ["#AI", "#Technology", "#Gaming", "#ContentCreator"]
            return {
                "platform": "youtube", 
                "trends": mock_trends,
                "hashtags": mock_hashtags,
                "status": "success",
                "data_source": "mock_data"
            }
        else:
            # Gerçek API kullan
            agent = TrendAgent()
            trends = agent.get_youtube_trends(api_key)
            return {"platform": "youtube", "trends": trends, "status": "success"}
            
    except Exception as e:
        # Hata durumunda mock data
        return {
            "platform": "youtube", 
            "trends": ["AI Technology", "Gaming Setup", "Content Creation"],
            "hashtags": ["#AI", "#Technology", "#Gaming"],
            "status": "error",
            "error": str(e),
            "data_source": "fallback"
        }

@router.get("/health")
async def health():
    return {"status": "ok", "service": "service_trend"}
