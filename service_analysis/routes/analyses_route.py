from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from modules.content_agent import ContentAgent
from modules.drive_client import get_drive_client

router = APIRouter(prefix="/analyzes", tags=["Analyzes"])
agent = ContentAgent()

# Request models
class ContentAnalysisRequest(BaseModel):
    keywords: Optional[List[str]] = None
    description: Optional[str] = None
    
class TextAnalysisRequest(BaseModel):
    title: Optional[str] = ""
    description: Optional[str] = ""
    keywords: Optional[List[str]] = None

@router.get("/drive")
async def analyze_drive(
    folder_id: Optional[str] = Query(None, description="Klasör ID (boş bırakılırsa SourceData klasörü kullanılır)")
):
    """Drive'dan dosyaları çekip analiz eder"""
    drive_client = get_drive_client()
    
    mime_types = ["image/jpeg", "image/png", "image/jpg", 
                  "video/mp4", "video/avi", "video/quicktime"]  # mov yerine quicktime
    
    try:
        files = drive_client.list_files(folder_id=folder_id, mime_types=mime_types)
        
        if not files:
            return {"results": [], "total_files": 0, "message": "Klasörde analiz edilebilir dosya bulunamadı"}

        results = []
        for f in files:
            file_path = drive_client.download_file(f["id"], f["name"])
            try:
                analysis = agent.analyze(file_path, f["mimeType"])
            except Exception as e:
                analysis = {"status": "error", "message": str(e)}
            
            results.append({
                "file": f["name"], 
                "file_id": f["id"],
                "mime_type": f["mimeType"],
                "analysis": analysis
            })
        
        return {"results": results, "total_files": len(results), "status": "success"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Drive analizi sırasında hata: {str(e)}")



@router.get("/drive/test")
async def drive_test():
    """Drive bağlantısını test eder"""
    drive_client = get_drive_client()
    
    try:
        # SourceData klasörünü bul veya ana dizindeki dosyaları listele
        files = drive_client.list_files()
        return {
            "success": True,
            "connection": "OK",
            "root_folder": drive_client.root_folder_name,
            "folder_id": drive_client.folder_id,
            "file_count": len(files),
            "sample_files": files[:5] if files else []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Drive bağlantı testi başarısız: {str(e)}")

@router.post("/drive/enhanced")
async def analyze_drive_enhanced(
    request: ContentAnalysisRequest,
    folder_id: Optional[str] = Query(None, description="Klasör ID")
):
    """
    Gelişmiş Drive analizi - metin işleme ile
    Çıktı: { "visual_summary": "...", "video_summary": "...", "keywords": [...] }
    """
    drive_client = get_drive_client()
    
    # Sadece image ve video mime type filtrele
    mime_types = ["image/jpeg", "image/png", "image/jpg", "video/mp4", "video/avi", "video/mov"]
    
    try:
        files = drive_client.list_files(folder_id=folder_id, mime_types=mime_types)
        
        if not files:
            return {
                "visual_summary": "No visual content found",
                "video_summary": "No video content found", 
                "keywords": [],
                "message": "Klasörde analiz edilebilir dosya bulunamadı"
            }

        # Dosyaları analiz et
        analysis_results = []
        for f in files:
            file_path = drive_client.download_file(f["id"], f["name"])
            analysis = agent.analyze(file_path, f["mimeType"])
            analysis_results.append({
                "file": f["name"], 
                "file_id": f["id"],
                "mime_type": f["mimeType"],
                "analysis": analysis
            })
        
        # Toplu analiz .
        enhanced_analysis = agent.analyze_content_batch(
            analysis_results=analysis_results,
            keywords=request.keywords,
            description=request.description
        )
        
        return enhanced_analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enhanced Drive analizi sırasında hata: {str(e)}")

@router.post("/text/keywords")
async def analyze_text_keywords(request: TextAnalysisRequest):
    """
    Sadece metin içeriği için ASO keyword analizi
    """
    try:
        result = agent.analyze_text_content(
            title=request.title,
            description=request.description,
            keywords=request.keywords
        )
        
        return {
            "keywords": result.get("keywords", []),
            "analysis": result.get("analysis", {}),
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text analizi sırasında hata: {str(e)}")

