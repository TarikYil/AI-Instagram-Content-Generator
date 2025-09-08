"""
Mikroservisler için HTTP client
"""
import requests
import httpx
import asyncio
from typing import Dict, List, Optional, Any
import streamlit as st
import time

class MicroserviceClient:
    def __init__(self):
        self.services = {
            "upload": "http://localhost:8001",
            "analysis": "http://localhost:8003", 
            "trend": "http://localhost:8002",
            "generation": "http://localhost:8004",
            "quality": "http://localhost:8005"
        }
        self.timeout = 120
    
    def check_service_health(self, service_name: str) -> bool:
        """Servis sağlığını kontrol et"""
        try:
            url = f"{self.services[service_name]}/health"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def check_all_services(self) -> Dict[str, bool]:
        """Tüm servislerin sağlığını kontrol et"""
        health_status = {}
        for service_name in self.services.keys():
            health_status[service_name] = self.check_service_health(service_name)
        return health_status
    
    # UPLOAD SERVICE
    def upload_images(self, files: List[bytes]) -> Dict[str, Any]:
        """Görselleri upload servisine yükle"""
        try:
            url = f"{self.services['upload']}/upload/images"
            
            # Multipart form data hazırla - 'images' field name kullan
            files_data = []
            for i, file_bytes in enumerate(files):
                files_data.append(('images', (f'image_{i}.jpg', file_bytes, 'image/jpeg')))
            
            # Form data ekle
            form_data = {'description': 'AI Instagram Content Generator Upload'}
            
            response = requests.post(url, files=files_data, data=form_data, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "success": False}
    
    # TREND SERVICE  
    def get_youtube_trends(self) -> Dict[str, Any]:
        """YouTube trend analizi al"""
        try:
            url = f"{self.services['trend']}/analyzes/youtube"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "success": False}
    
    # ANALYSIS SERVICE
    def analyze_drive_content(self, folder_id: Optional[str] = None, keywords: Optional[List[str]] = None) -> Dict[str, Any]:
        """Drive içeriği analiz et (enhanced format)"""
        try:
            url = f"{self.services['analysis']}/analyzes/drive/enhanced"
            
            # Request body
            request_data = {
                "keywords": keywords or [],
                "description": "AI Instagram Content Analysis"
            }
            
            # Query parameter
            params = {}
            if folder_id:
                params["folder_id"] = folder_id
            
            response = requests.post(
                url, 
                json=request_data, 
                params=params, 
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def analyze_text_keywords(self, title: str, description: str, keywords: Optional[List[str]] = None) -> Dict[str, Any]:
        """Text içeriği için ASO keyword analizi"""
        try:
            url = f"{self.services['analysis']}/analyzes/text/keywords"
            request_data = {
                "title": title,
                "description": description,
                "keywords": keywords or []
            }
            
            response = requests.post(url, json=request_data, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "success": False}
    
    # GENERATION SERVICE
    def generate_instagram_content(self, visual_summary: str, keywords: List[str], 
                                 video_summary: str = "", trends: Optional[List[str]] = None,
                                 style: str = "modern") -> Dict[str, Any]:
        """Instagram içeriği üret"""
        try:
            url = f"{self.services['generation']}/generate/poster"
            request_data = {
                "visual_summary": visual_summary,
                "video_summary": video_summary,
                "keywords": keywords,
                "trends": trends or [],
                "poster_style": style,
                "include_trends": bool(trends)
            }
            
            response = requests.post(url, json=request_data, timeout=180)  # 3 dakika timeout
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def get_generation_styles(self) -> Dict[str, Any]:
        """Mevcut generation style'larını al"""
        try:
            url = f"{self.services['generation']}/generate/poster/styles"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def download_generated_image(self, filename: str) -> bytes:
        """Üretilen görseli indir"""
        try:
            url = f"{self.services['generation']}/generate/poster/download/{filename}"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.content
        except Exception as e:
            st.error(f"Görsel indirilemedi: {e}")
            return b""
    
    # QUALITY SERVICE
    def assess_image_quality(self, image_path: str, prompt: str) -> Dict[str, Any]:
        """Görsel kalitesi değerlendir"""
        try:
            url = f"{self.services['quality']}/quality/assess"
            request_data = {
                "image_path": image_path,
                "prompt": prompt
            }
            
            response = requests.post(url, json=request_data, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def finalize_content(self, image_path: str, original_prompt: str, 
                        style: str = "modern", platform: str = "instagram",
                        max_hashtags: int = 15) -> Dict[str, Any]:
        """İçeriği finalize et (kalite bazlı hashtag ve caption)"""
        try:
            url = f"{self.services['quality']}/quality/finalize"
            request_data = {
                "image_path": image_path,
                "original_prompt": original_prompt,
                "style": style,
                "platform": platform,
                "max_hashtags": max_hashtags
            }
            
            response = requests.post(url, json=request_data, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "success": False}

# Global client instance
@st.cache_resource
def get_microservice_client():
    return MicroserviceClient()
