from helpers.image_helper import analyze_image
from helpers.video_helper import analyze_video
from helpers.text_helper import get_text_processor
from typing import List, Dict, Any, Optional

class ContentAgent:
    def __init__(self):
        self.text_processor = get_text_processor()
    
    def analyze(self, file_path: str, mime_type: str):
        """Tek dosya analizi - eski format için uyumluluk"""
        if mime_type.startswith("image/"):
            return analyze_image(file_path)
        elif mime_type.startswith("video/"):
            return analyze_video(file_path)
        else:
            return {"error": "Unsupported file type"}
    
    def analyze_content_batch(self, analysis_results: List[Dict[str, Any]], 
                            keywords: List[str] = None, 
                            description: str = None) -> Dict[str, Any]:
        """
        Toplu içerik analizi - yeni format
        
        Args:
            analysis_results: analyze() sonuçlarının listesi
            keywords: Mevcut ASO keyword'leri
            description: Mevcut açıklama metni
            
        Returns:
            {
                "visual_summary": "...",
                "video_summary": "...", 
                "keywords": [...],
                "detailed_analysis": {...}
            }
        """
        try:
            # Caption'ları topla
            visual_captions = []
            video_captions = []
            
            for result in analysis_results:
                analysis = result.get("analysis", {})
                if analysis.get("type") == "image" and analysis.get("status") == "success":
                    caption = analysis.get("caption", "")
                    if caption:
                        visual_captions.append(caption)
                        
                elif analysis.get("type") == "video" and analysis.get("status") == "success":
                    captions = analysis.get("captions", [])
                    for cap_info in captions:
                        if isinstance(cap_info, dict):
                            caption = cap_info.get("caption", "")
                        else:
                            caption = str(cap_info)
                        
                        if caption and not caption.startswith("Error:"):
                            video_captions.append(caption)
            
            # İçerik özetlerini oluştur
            content_summary = self.text_processor.summarize_content(
                visual_captions=visual_captions,
                video_captions=video_captions
            )
            
            # ASO keyword analizi
            all_content_text = " ".join(visual_captions + video_captions)
            if description:
                all_content_text += f" {description}"
            
            aso_analysis = self.text_processor.analyze_aso_keywords(
                title="",  # Title yoksa boş
                description=all_content_text,
                current_keywords=keywords
            )
            
            return {
                "visual_summary": content_summary.get("visual_summary", ""),
                "video_summary": content_summary.get("video_summary", ""),
                "keywords": aso_analysis.get("recommended_keywords", []),
                "detailed_analysis": {
                    "total_images": len(visual_captions),
                    "total_videos": len(video_captions),
                    "visual_captions": visual_captions,
                    "video_captions": video_captions,
                    "aso_analysis": aso_analysis,
                    "content_summary": content_summary
                }
            }
            
        except Exception as e:
            return {
                "visual_summary": f"Analysis failed: {str(e)}",
                "video_summary": f"Analysis failed: {str(e)}",
                "keywords": [],
                "detailed_analysis": {"error": str(e)}
            }
    
    def analyze_text_content(self, title: str = "", description: str = "", 
                           keywords: List[str] = None) -> Dict[str, Any]:
        """Sadece metin içeriği analiz et"""
        try:
            aso_analysis = self.text_processor.analyze_aso_keywords(
                title=title,
                description=description,
                current_keywords=keywords or []
            )
            
            return {
                "keywords": aso_analysis.get("recommended_keywords", []),
                "analysis": aso_analysis
            }
            
        except Exception as e:
            return {
                "keywords": [],
                "analysis": {"error": str(e)}
            }
