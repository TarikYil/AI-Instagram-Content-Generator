from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ValidationError
from helpers.diffusion_image_generator import get_diffusion_generator
import logging
import json
import os

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/generate", tags=["Generation"])

# Request models
class ImageGenerationRequest(BaseModel):
    visual_summary: str
    video_summary: Optional[str] = ""
    keywords: List[str]
    trends: Optional[List[str]] = []
    hashtags: Optional[List[str]] = []
    poster_style: Optional[str] = "modern"  # modern, gaming, minimal, trendy
    include_trends: Optional[bool] = True

# Poster generation endpoint

# Poster generation endpoint

@router.post("/poster")
async def generate_instagram_poster(raw_request: Request, request: ImageGenerationRequest = None):
    """
    Instagram poster/görsel oluştur
    """
    try:
        # Raw request body'yi log et
        body_bytes = await raw_request.body()
        body_str = body_bytes.decode('utf-8')
        print(f"🖼️ [POSTER DEBUG] Raw request body: {body_str}")
        logger.info(f"🖼️ Poster generation request: {body_str}")
        
        # JSON parse kontrolü
        try:
            body_json = json.loads(body_str) if body_str else {}
            print(f"🖼️ [POSTER DEBUG] Parsed JSON: {body_json}")
        except json.JSONDecodeError as json_err:
            print(f"❌ [POSTER DEBUG] JSON parse error: {json_err}")
            raise HTTPException(status_code=400, detail=f"Invalid JSON: {json_err}")
        
        # Request validation
        if request is None:
            try:
                request = ImageGenerationRequest(**body_json)
                print(f"✅ [POSTER DEBUG] Request validation successful")
            except ValidationError as val_err:
                print(f"❌ [POSTER DEBUG] Validation error: {val_err}")
                raise HTTPException(status_code=400, detail=f"Validation error: {val_err}")
        
        print(f"🎨 [POSTER DEBUG] Creating poster - Style: {request.poster_style}")
        print(f"🎨 [POSTER DEBUG] Visual: {request.visual_summary[:50]}...")
        print(f"🎨 [POSTER DEBUG] Keywords: {request.keywords}")
        
        diffusion_generator = get_diffusion_generator()
        
        # Content data hazırla
        content_data = {
            "visual_summary": request.visual_summary,
            "video_summary": request.video_summary,
            "keywords": request.keywords,
            "hashtags": request.hashtags
        }
        
        # Trend data (eğer varsa)
        trend_data = None
        if request.include_trends and request.trends:
            trend_data = {
                "trends": request.trends
            }
        
        # Diffusion generator ile oluştur
        image_path = diffusion_generator.generate_instagram_image(
            content_data=content_data,
            trend_data=trend_data,
            style=request.poster_style
        )
        
        print(f"✅ [POSTER DEBUG] Poster created: {image_path}")
        logger.info(f"Instagram poster created: {image_path}")
        
        # Dosya adını çıkar
        filename = os.path.basename(image_path)
        
        return {
            "success": True,
            "poster_created": True,
            "image_path": image_path,
            "filename": filename,
            "download_url": f"/generate/poster/download/{filename}",
            "metadata": {
                "style": request.poster_style,
                "include_trends": request.include_trends,
                "generation_timestamp": _get_timestamp()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [POSTER DEBUG] Unexpected error: {e}")
        logger.error(f"❌ Poster generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Poster generation failed: {str(e)}")

@router.get("/poster/download/{filename}")
async def download_poster(filename: str):
    """
    Oluşturulan poster'ı indir
    """
    try:
        tmp_dir = os.path.join(os.path.dirname(__file__), "..", "tmp")
        file_path = os.path.join(tmp_dir, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Poster dosyası bulunamadı")
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='image/png'
        )
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Poster dosyası bulunamadı")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download error: {str(e)}")

# Poster styles endpoint

@router.get("/poster/styles")
async def get_poster_styles():
    """
    Mevcut poster style'larını listele
    """
    styles = {
        "modern": {
            "name": "Modern",
            "description": "Dark theme with coral and teal accents",
            "colors": ["#1a1a1a", "#FF6B6B", "#4ECDC4", "#FFE66D"],
            "best_for": "Professional content, tech, business"
        },
        "gaming": {
            "name": "Gaming",
            "description": "Gaming style with neon colors and effects",
            "colors": ["#0D1117", "#FF0080", "#00D9FF", "#FFFF00"],
            "best_for": "Gaming content, mobile games, entertainment"
        },
        "minimal": {
            "name": "Minimal",
            "description": "Clean and minimal design",
            "colors": ["#F8F9FA", "#2C3E50", "#3498DB", "#E74C3C"],
            "best_for": "Professional content, education, clean aesthetics"
        },
        "trendy": {
            "name": "Trendy",
            "description": "Gradient background with trendy elements",
            "colors": ["#FF6B6B", "#6BB6FF", "#FFE66D", "#FFFFFF"],
            "best_for": "Trending content, social media, viral posts"
        }
    }
    
    return {
        "available_styles": styles,
        "default_style": "modern"
    }

# Health check endpoint
@router.get("/health")
async def health():
    return {"status": "ok", "service": "service_generation"}

def _get_timestamp() -> str:
    """Current timestamp döndür"""
    from datetime import datetime
    return datetime.now().isoformat()
