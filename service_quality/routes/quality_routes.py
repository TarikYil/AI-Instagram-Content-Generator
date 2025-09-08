from fastapi import APIRouter, HTTPException, Body
from typing import Optional, Dict, Any
from pydantic import BaseModel
from modules.quality_agent import get_quality_agent
from modules.finalization_agent import get_finalization_agent
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/quality", tags=["Quality Assessment"])

# Request models - sadece gerekli olanlar
class ImageQualityRequest(BaseModel):
    image_path: str
    prompt: Optional[str] = None

class QualityFinalizationRequest(BaseModel):
    image_path: str
    original_prompt: str
    style: Optional[str] = "modern"
    platform: Optional[str] = "instagram"
    max_hashtags: Optional[int] = 15

# Core endpoints - sadece kalite skoru ve finalization
@router.post("/assess")
async def assess_image_quality(request: ImageQualityRequest):
    """
    Görsel kalite skoru hesaplama - CLIP + Aesthetic + Technical
    """
    try:
        print(f"🔍 [QUALITY] Quality assessment request")
        print(f"📁 [QUALITY] Image: {request.image_path}")
        print(f"📝 [QUALITY] Prompt: {request.prompt}")
        
        quality_agent = get_quality_agent()
        
        # Quality assessment
        assessment = quality_agent.assess_image_quality(
            image_path=request.image_path,
            prompt=request.prompt
        )
        
        return {
            "success": True,
            "quality_assessment": assessment,
            "metadata": {
                "assessment_timestamp": datetime.now().isoformat(),
                "service": "service_quality"
            }
        }
        
    except Exception as e:
        logger.error(f"Quality assessment failed: {e}")
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")

@router.post("/finalize")
async def finalize_content_with_quality(request: QualityFinalizationRequest):
    """
    Görsel kalite skoruna göre content finalization ve hashtag generation
    """
    try:
        print(f"🎯 [FINALIZE] Content finalization request")
        print(f"📁 [FINALIZE] Image: {request.image_path}")
        print(f"📝 [FINALIZE] Prompt: {request.original_prompt}")
        print(f"🎨 [FINALIZE] Style: {request.style}")
        
        quality_agent = get_quality_agent()
        finalization_agent = get_finalization_agent()
        
        # 1. Quality assessment
        quality_assessment = quality_agent.assess_image_quality(
            image_path=request.image_path,
            prompt=request.original_prompt
        )
        
        # 2. Quality-based hashtag generation
        hashtags = finalization_agent.generate_quality_hashtags_only(
            quality_assessment=quality_assessment,
            style=request.style,
            max_hashtags=request.max_hashtags
        )
        
        # 3. Quality-based caption
        caption = finalization_agent._generate_quality_caption(
            original_prompt=request.original_prompt,
            quality_assessment=quality_assessment,
            style=request.style,
            platform=request.platform
        )
        
        return {
            "success": True,
            "finalized_content": {
                "caption": caption,
                "hashtags": hashtags,
                "hashtag_count": len(hashtags)
            },
            "quality_scores": {
                "overall_score": quality_assessment.get("overall_score", {}).get("overall_score", 0),
                "clip_score": quality_assessment.get("overall_score", {}).get("raw_scores", {}).get("clip_score", 0),
                "aesthetic_score": quality_assessment.get("overall_score", {}).get("raw_scores", {}).get("aesthetic_score", 0),
                "quality_level": quality_assessment.get("overall_score", {}).get("quality_level", "unknown")
            },
            "metadata": {
                "finalization_timestamp": datetime.now().isoformat(),
                "style": request.style,
                "platform": request.platform
            }
        }
        
    except Exception as e:
        logger.error(f"Content finalization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Finalization failed: {str(e)}")

@router.get("/health")
async def health():
    return {"status": "ok", "service": "service_quality"}