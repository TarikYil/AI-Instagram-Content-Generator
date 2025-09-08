import os
import logging
from typing import Dict, Any, List, Optional
from jinja2 import Template
import json
from dotenv import load_dotenv
from datetime import datetime
import uuid

# .env dosyasını yükle
load_dotenv()

logger = logging.getLogger(__name__)

class ContentGenerator:
    def __init__(self):
        logger.info("✅ Content Generator initialized (template-based only)")
        
    def generate_instagram_caption(self, 
                                 visual_summary: str,
                                 video_summary: str,
                                 keywords: List[str],
                                 trends: List[str],
                                 hashtags: List[str],
                                 style: str = "engaging") -> Dict[str, Any]:
        """Instagram caption üret"""
        
        print(f"🎨 [GEN DEBUG] Caption generation started")
        print(f"🎨 [GEN DEBUG] Style: {style}")
        print(f"🎨 [GEN DEBUG] Visual: {visual_summary[:50]}...")
        print(f"🎨 [GEN DEBUG] Keywords: {keywords}")
        print(f"🎨 [GEN DEBUG] Trends: {trends}")
        print(f"🎨 [GEN DEBUG] Hashtags: {hashtags}")
        
        logger.info(f"🎨 Caption üretimi başlatılıyor - Style: {style}")
        
        # Template-based generation
        print(f"🎨 [GEN DEBUG] Starting template-based generation...")
        template_result = self._generate_template_caption(
            visual_summary, video_summary, keywords, trends, hashtags, style
        )
        print(f"🎨 [GEN DEBUG] Template generation completed: {template_result is not None}")
        
        result = {
            "template_caption": template_result,
            "recommended": template_result,
            "generation_method": "template"
        }
        
        # Generated content'i tmp klasörüne kaydet
        self._save_to_tmp(result, visual_summary, keywords, style)
        
        return result
    
    def _generate_template_caption(self, visual_summary: str, video_summary: str, 
                                 keywords: List[str], trends: List[str], 
                                 hashtags: List[str], style: str) -> Dict[str, Any]:
        """Template tabanlı caption üretimi"""
        
        # Style'a göre template seç
        templates = {
            "engaging": """🎮 {{content_description}}

✨ {{highlight_features}}

{{call_to_action}}

{{hashtags}}""",
            
            "professional": """{{content_description}}

Key features:
{{features_list}}

{{hashtags}}""",
            
            "casual": """{{casual_intro}} {{content_description}} 

{{fun_element}}

{{hashtags}}""",
            
            "trendy": """{{trend_hook}} 

{{content_description}}

{{trend_connection}}

{{hashtags}}"""
        }
        
        template_str = templates.get(style, templates["engaging"])
        template = Template(template_str)
        
        # Template variables
        content_desc = self._create_content_description(visual_summary, video_summary)
        features = self._extract_features(keywords)
        hashtag_str = " ".join([f"#{tag}" for tag in hashtags[:10]])
        
        variables = {
            "content_description": content_desc,
            "highlight_features": self._create_highlights(features, trends),
            "call_to_action": self._get_call_to_action(style),
            "hashtags": hashtag_str,
            "features_list": "\n".join([f"• {feature}" for feature in features[:5]]),
            "casual_intro": self._get_casual_intro(),
            "fun_element": self._get_fun_element(keywords),
            "trend_hook": self._get_trend_hook(trends),
            "trend_connection": self._get_trend_connection(trends, keywords)
        }
        
        caption = template.render(**variables)
        
        return {
            "caption": caption.strip(),
            "word_count": len(caption.split()),
            "hashtag_count": len(hashtags),
            "style": style,
            "method": "template"
        }
    
    def _generate_openai_caption(self, visual_summary: str, video_summary: str,
                               keywords: List[str], trends: List[str],
                               hashtags: List[str], style: str) -> Optional[Dict[str, Any]]:
        """OpenAI ile caption üretimi"""
        try:
            prompt = self._create_ai_prompt(visual_summary, video_summary, keywords, trends, hashtags, style)
            
            response = self.openai_client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert Instagram content creator specializing in gaming content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            caption = response.choices[0].message.content.strip()
            
            return {
                "caption": caption,
                "word_count": len(caption.split()),
                "hashtag_count": len(hashtags),
                "style": style,
                "method": "openai"
            }
            
        except Exception as e:
            logger.error(f"❌ OpenAI caption generation hatası: {e}")
            return None
    
    def _generate_gemini_caption(self, visual_summary: str, video_summary: str,
                               keywords: List[str], trends: List[str],
                               hashtags: List[str], style: str) -> Optional[Dict[str, Any]]:
        """Google Gemini ile caption üretimi"""
        try:
            prompt = self._create_ai_prompt(visual_summary, video_summary, keywords, trends, hashtags, style)
            
            response = self.gemini_client.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 300,
                    "top_p": 0.8,
                    "top_k": 40
                }
            )
            
            caption = response.text.strip()
            
            return {
                "caption": caption,
                "word_count": len(caption.split()),
                "hashtag_count": len(hashtags),
                "style": style,
                "method": "gemini"
            }
            
        except Exception as e:
            logger.error(f"❌ Gemini caption generation hatası: {e}")
            return None
    
    def _create_ai_prompt(self, visual_summary: str, video_summary: str,
                         keywords: List[str], trends: List[str], 
                         hashtags: List[str], style: str) -> str:
        """AI için prompt oluştur"""
        
        prompt = f"""Create an Instagram caption for gaming content with the following details:

Visual Content: {visual_summary}
Video Content: {video_summary}
Keywords: {', '.join(keywords)}
Current Trends: {', '.join(trends)}
Style: {style}

Requirements:
- Write in Turkish
- Use an {style} tone
- Include emojis appropriately
- Make it engaging for Instagram audience
- Focus on gaming/mobile game content
- Length: 100-200 words
- End with these hashtags: {' '.join([f'#{tag}' for tag in hashtags[:8]])}

Generate a compelling Instagram caption:"""

        return prompt
    
    def _create_content_description(self, visual_summary: str, video_summary: str) -> str:
        """İçerik açıklaması oluştur"""
        parts = []
        if visual_summary and visual_summary != "Content analysis failed":
            parts.append(f"Görsel: {visual_summary}")
        if video_summary and video_summary != "Content analysis failed":
            parts.append(f"Video: {video_summary}")
        
        if not parts:
            return "Harika oyun içeriği!"
        
        return " | ".join(parts)
    
    def _extract_features(self, keywords: List[str]) -> List[str]:
        """Keyword'lerden özellik çıkar"""
        gaming_features = {
            "adventure": "Macera dolu hikaye",
            "puzzle": "Zeka oyunları",
            "graphics": "Muhteşem grafikler", 
            "mobile": "Mobil uyumlu",
            "game": "Eğlenceli oynanış",
            "action": "Aksiyon dolu",
            "strategy": "Strateji gerektiren"
        }
        
        features = []
        for keyword in keywords[:5]:
            if keyword.lower() in gaming_features:
                features.append(gaming_features[keyword.lower()])
            else:
                features.append(keyword.capitalize())
        
        return features
    
    def _create_highlights(self, features: List[str], trends: List[str]) -> str:
        """Öne çıkan özellikleri oluştur"""
        highlights = features[:3]
        if trends:
            highlights.extend(trends[:2])
        
        return " • ".join(highlights[:4])
    
    def _get_call_to_action(self, style: str) -> str:
        """Call to action oluştur"""
        ctas = {
            "engaging": "Hemen oyna ve deneyimini paylaş! 👇",
            "professional": "Daha fazla bilgi için yorumlarda bize yazın.",
            "casual": "Sen de dene ve arkadaşlarınla paylaş! 🎮",
            "trendy": "Trend olan bu oyunu kaçırma! 🔥"
        }
        return ctas.get(style, ctas["engaging"])
    
    def _get_casual_intro(self) -> str:
        """Casual intro oluştur"""
        intros = ["Bugün keşfettim:", "Bak ne buldum:", "Bu oyun harika:", "Denedim ve çok beğendim:"]
        import random
        return random.choice(intros)
    
    def _get_fun_element(self, keywords: List[str]) -> str:
        """Eğlenceli element ekle"""
        if "puzzle" in [k.lower() for k in keywords]:
            return "🧩 Puzzle severler buraya!"
        elif "adventure" in [k.lower() for k in keywords]:
            return "🗺️ Macera zamanı!"
        else:
            return "🎮 Oyun zamanı!"
    
    def _get_trend_hook(self, trends: List[str]) -> str:
        """Trend hook oluştur"""
        if trends:
            return f"🔥 {trends[0]} trendi devam ediyor!"
        return "🔥 Yeni trend keşfettim!"
    
    def _get_trend_connection(self, trends: List[str], keywords: List[str]) -> str:
        """Trend bağlantısı oluştur"""
        if trends and keywords:
            return f"#{trends[0]} ile {keywords[0]} kombinasyonu mükemmel! 💯"
        return "Bu kombinasyon harika! 💯"
    
    def _save_to_tmp(self, result: Dict[str, Any], visual_summary: str, keywords: List[str], style: str):
        """Generated content'i tmp klasörüne kaydet"""
        try:
            # Unique filename oluştur
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            filename = f"caption_{timestamp}_{unique_id}.json"
            
            # tmp klasörü path
            tmp_dir = os.path.join(os.path.dirname(__file__), "..", "tmp")
            os.makedirs(tmp_dir, exist_ok=True)
            
            # Save data
            save_data = {
                "timestamp": datetime.now().isoformat(),
                "input": {
                    "visual_summary": visual_summary,
                    "keywords": keywords,
                    "style": style
                },
                "output": result,
                "filename": filename
            }
            
            # JSON dosyasına kaydet
            filepath = os.path.join(tmp_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            print(f"💾 [SAVE] Generated content saved: {filename}")
            logger.info(f"Generated content saved to tmp: {filename}")
            
        except Exception as e:
            print(f"⚠️ [SAVE ERROR] Failed to save to tmp: {e}")
            logger.warning(f"Failed to save generated content to tmp: {e}")

# Singleton instance
_content_generator = None

def get_content_generator() -> ContentGenerator:
    global _content_generator
    if _content_generator is None:
        _content_generator = ContentGenerator()
    return _content_generator
