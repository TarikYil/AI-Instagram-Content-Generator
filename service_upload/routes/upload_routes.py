from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
from helpers.file_utils import save_temp_file
from modules.drive_client import get_drive_client

router = APIRouter(prefix="/upload", tags=["Upload"])

@router.post("/images")
async def upload_images(
    images: List[UploadFile] = File(...),
    description: str = Form("Uploaded images")
):
    """
    Sadece görsel yükleme - basitleştirilmiş route
    """
    try:
        drive_client = get_drive_client()
        result = {"images": [], "description": description}

        # Images upload
        for img in images:
            img_path = save_temp_file(img)
            upload_result = drive_client.upload_file(img_path, img.filename)
            result["images"].append(upload_result)

        return {
            "success": True, 
            "uploaded_count": len(result["images"]),
            "assets": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/health")
async def health():
    return {"status": "ok", "service": "service_upload"}