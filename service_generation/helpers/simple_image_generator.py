import os
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging
from PIL import Image, ImageDraw, ImageFont
import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class SimpleImageGenerator:
    def __init__(self):
        self.poster_size = (1080, 1080)  # Instagram square format
        
    def generate_instagram_image(self, 
                                content_data: Dict[str, Any],
                                trend_data: Optional[Dict[str, Any]] = None,
                                style: str = "modern") -> str:
        """
        Basit image generation - gerçek AI modeli ile
        """
        try:
            print(f"\n🎨 [IMAGE GEN] Starting Instagram image generation...")
            print(f"🎨 [IMAGE GEN] Style: {style}")
            print(f"📊 [IMAGE GEN] Content data received")
            
            # Input data debug
            visual_summary = content_data.get('visual_summary', 'amazing content')
            keywords = content_data.get('keywords', [])
            hashtags = content_data.get('hashtags', [])
            
            print(f"📋 [INPUT] Visual Summary: {visual_summary}")
            print(f"📋 [INPUT] Keywords: {keywords}")
            print(f"📋 [INPUT] Hashtags: {hashtags}")
            
            if trend_data:
                trends = trend_data.get('trends', [])
                print(f"📈 [INPUT] Trends: {trends}")
            
            # AI prompt oluştur
            prompt = self._create_ai_prompt(content_data, trend_data, style)
            print(f"✨ [PROMPT] Generated AI prompt: {prompt}")
            
            # AI image generation dene
            ai_image = self._try_ai_generation(prompt)
            
            if ai_image:
                print(f"🤖 [AI] AI image generation successful!")
                instagram_image = self._format_for_instagram(ai_image, content_data, style)
            else:
                print(f"🎨 [FALLBACK] Using enhanced text-based generation...")
                instagram_image = self._create_enhanced_poster(content_data, trend_data, style)
            
            # Save image
            saved_path = self._save_image(instagram_image, f"{style}_ai_generated")
            
            print(f"🎉 [SUCCESS] Image generation completed!")
            print(f"📁 [SUCCESS] Saved to: {saved_path}")
            
            return saved_path
            
        except Exception as e:
            print(f"❌ [ERROR] Image generation failed: {e}")
            logger.error(f"Image generation failed: {e}")
            return self._create_fallback_image(content_data, style)
    
    def _create_ai_prompt(self, content_data: Dict[str, Any], 
                         trend_data: Optional[Dict[str, Any]], 
                         style: str) -> str:
        """AI image generation için prompt oluştur"""
        
        visual_summary = content_data.get('visual_summary', 'amazing content')
        keywords = content_data.get('keywords', [])
        
        # Style-based prompt
        style_prompts = {
            "modern": "modern minimalist design, clean aesthetics, professional layout",
            "gaming": "gaming aesthetic, neon colors, futuristic design, cyberpunk style",
            "minimal": "minimal design, white background, clean typography",
            "trendy": "trendy social media design, vibrant colors, instagram style"
        }
        
        style_desc = style_prompts.get(style, style_prompts["modern"])
        keywords_text = ", ".join(keywords[:5]) if keywords else ""
        
        prompt = f"{style_desc}, {visual_summary}, {keywords_text}, high quality, digital art, social media ready"
        
        return prompt
    
    def _try_ai_generation(self, prompt: str) -> Optional[Image.Image]:
        """AI image generation denemesi - placeholder"""
        
        print(f"🤖 [AI] Attempting AI image generation...")
        print(f"📝 [AI] Prompt: {prompt}")
        
        # Bu kısımda gerçek AI API'si kullanılabilir
        # Şimdilik None döndürüp fallback'e geçiyoruz
        
        try:
            # Placeholder - burada gerçek AI API çağrısı olacak
            # Örnek: DALL-E, Midjourney API, vs.
            
            print(f"⚠️ [AI] AI service not configured, using fallback")
            return None
            
        except Exception as e:
            print(f"❌ [AI] AI generation failed: {e}")
            return None
    
    def _create_enhanced_poster(self, content_data: Dict[str, Any], 
                               trend_data: Optional[Dict[str, Any]], 
                               style: str) -> Image.Image:
        """Enhanced text-based poster - gerçek tasarım ile"""
        
        print(f"🎨 [ENHANCED] Creating enhanced poster...")
        
        # Style-based colors
        color_schemes = {
            "modern": {
                "bg": "#1a1a1a", "primary": "#FF6B6B", "secondary": "#4ECDC4", 
                "text": "#FFFFFF", "accent": "#FFE66D"
            },
            "gaming": {
                "bg": "#0D1117", "primary": "#FF0080", "secondary": "#00D9FF", 
                "text": "#FFFFFF", "accent": "#FFFF00"
            },
            "minimal": {
                "bg": "#F8F9FA", "primary": "#2C3E50", "secondary": "#3498DB", 
                "text": "#2C3E50", "accent": "#E74C3C"
            },
            "trendy": {
                "bg": "#FF6B6B", "primary": "#FFFFFF", "secondary": "#FFE66D", 
                "text": "#2C3E50", "accent": "#6BB6FF"
            }
        }
        
        colors = color_schemes.get(style, color_schemes["modern"])
        
        # Create image with gradient background
        img = self._create_gradient_background(colors["bg"], colors["secondary"])
        draw = ImageDraw.Draw(img)
        
        # Title from content
        title = self._extract_smart_title(content_data)
        print(f"📝 [ENHANCED] Title: {title}")
        
        # Enhanced layout
        self._draw_enhanced_layout(draw, title, content_data, colors, style)
        
        return img
    
    def _create_gradient_background(self, color1: str, color2: str) -> Image.Image:
        """Gradient background oluştur"""
        
        img = Image.new('RGB', self.poster_size, color=color1)
        
        # Simple gradient effect
        draw = ImageDraw.Draw(img)
        
        # Convert hex to RGB
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        rgb1 = hex_to_rgb(color1)
        rgb2 = hex_to_rgb(color2)
        
        # Create gradient
        for y in range(self.poster_size[1]):
            ratio = y / self.poster_size[1]
            r = int(rgb1[0] * (1 - ratio) + rgb2[0] * ratio)
            g = int(rgb1[1] * (1 - ratio) + rgb2[1] * ratio)
            b = int(rgb1[2] * (1 - ratio) + rgb2[2] * ratio)
            
            draw.line([(0, y), (self.poster_size[0], y)], fill=(r, g, b))
        
        return img
    
    def _extract_smart_title(self, content_data: Dict[str, Any]) -> str:
        """Akıllı başlık çıkarma"""
        
        visual_summary = content_data.get('visual_summary', '')
        keywords = content_data.get('keywords', [])
        
        # Visual summary'den akıllı başlık
        if visual_summary:
            words = visual_summary.split()
            
            # İlk 3-4 anlamlı kelimeyi al
            meaningful_words = []
            for word in words[:6]:
                if len(word) > 3 and word.lower() not in ['ile', 'için', 'olan', 'bir', 'bu', 'şu']:
                    meaningful_words.append(word.title())
                if len(meaningful_words) >= 3:
                    break
            
            if meaningful_words:
                return ' '.join(meaningful_words)
        
        # Keywords'den başlık
        if keywords:
            return ' '.join(keywords[:3]).title()
        
        return "AI Generated Content"
    
    def _draw_enhanced_layout(self, draw, title: str, content_data: Dict[str, Any], 
                             colors: dict, style: str):
        """Enhanced layout çizimi"""
        
        # Header area
        self._draw_header_section(draw, title, colors, style)
        
        # Content area
        self._draw_content_section(draw, content_data, colors)
        
        # Keywords section
        keywords = content_data.get('keywords', [])
        if keywords:
            self._draw_keywords_section(draw, keywords, colors)
        
        # Footer
        self._draw_footer_section(draw, content_data.get('hashtags', []), colors)
    
    def _draw_header_section(self, draw, title: str, colors: dict, style: str):
        """Header section çiz"""
        
        # Background rectangle for title
        draw.rectangle([(50, 100), (1030, 250)], fill=colors["primary"], outline=colors["accent"], width=3)
        
        # Title text
        self._draw_text_centered(draw, title, (540, 175), 48, colors["text"])
        
        # Style indicator
        style_emoji = {"gaming": "🎮", "modern": "💼", "minimal": "✨", "trendy": "🔥"}
        emoji = style_emoji.get(style, "🎨")
        self._draw_text_centered(draw, emoji, (100, 175), 60, colors["accent"])
    
    def _draw_content_section(self, draw, content_data: Dict[str, Any], colors: dict):
        """Content section çiz"""
        
        visual_summary = content_data.get('visual_summary', 'Amazing content!')
        
        # Content background
        draw.rectangle([(100, 300), (980, 500)], fill=colors["secondary"], outline=colors["primary"], width=2)
        
        # Wrapped text
        self._draw_wrapped_text(draw, visual_summary, (150, 350), 32, colors["text"], 780)
    
    def _draw_keywords_section(self, draw, keywords: List[str], colors: dict):
        """Keywords section çiz"""
        
        y_start = 550
        
        for i, keyword in enumerate(keywords[:6]):
            col = i % 3
            row = i // 3
            
            x = 200 + col * 280
            y = y_start + row * 80
            
            # Keyword badge
            draw.rounded_rectangle([(x-60, y-25), (x+60, y+25)], radius=15, 
                                 fill=colors["accent"], outline=colors["primary"], width=2)
            
            self._draw_text_centered(draw, f"#{keyword}", (x, y), 20, colors["text"])
    
    def _draw_footer_section(self, draw, hashtags: List[str], colors: dict):
        """Footer section çiz"""
        
        # Footer background
        draw.rectangle([(50, 850), (1030, 950)], fill=colors["primary"], outline=colors["accent"], width=2)
        
        # Hashtags
        hashtag_text = " ".join([f"#{tag}" for tag in hashtags[:8]])
        self._draw_wrapped_text(draw, hashtag_text, (100, 875), 24, colors["text"], 830)
        
        # Branding
        self._draw_text_centered(draw, "AI Generated Instagram Content", (540, 1000), 20, colors["text"])
    
    def _draw_text_centered(self, draw, text: str, position: tuple, size: int, color: str):
        """Centered text çiz"""
        try:
            bbox = draw.textbbox((0, 0), text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = position[0] - text_width // 2
            y = position[1] - text_height // 2
            
            draw.text((x, y), text, fill=color)
        except Exception:
            draw.text(position, text[:30], fill=color)
    
    def _draw_wrapped_text(self, draw, text: str, position: tuple, size: int, color: str, max_width: int):
        """Wrapped text çiz"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if len(test_line) * (size * 0.6) <= max_width:  # Rough estimate
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw lines
        y_offset = 0
        line_height = size + 8
        
        for line in lines[:4]:  # Max 4 lines
            draw.text((position[0], position[1] + y_offset), line, fill=color)
            y_offset += line_height
    
    def _format_for_instagram(self, base_image: Image.Image, 
                             content_data: Dict[str, Any], 
                             style: str) -> Image.Image:
        """AI image'i Instagram formatına dönüştür"""
        
        # Instagram square format
        instagram_img = Image.new('RGB', self.poster_size, color='white')
        
        # Base image'i resize et
        base_image = base_image.resize((800, 800), Image.Resampling.LANCZOS)
        
        # Center paste
        x = (self.poster_size[0] - 800) // 2
        y = (self.poster_size[1] - 800) // 2 - 50
        
        instagram_img.paste(base_image, (x, y))
        
        # Text overlay
        draw = ImageDraw.Draw(instagram_img)
        
        # Title overlay
        title = self._extract_smart_title(content_data)
        self._draw_text_centered(draw, title, (540, 950), 36, 'black')
        
        return instagram_img
    
    def _extract_smart_title(self, content_data: Dict[str, Any]) -> str:
        """Smart title extraction"""
        
        visual_summary = content_data.get('visual_summary', '')
        keywords = content_data.get('keywords', [])
        
        if visual_summary:
            words = visual_summary.split()[:4]
            if len(words) >= 2:
                return ' '.join(words).title()
        
        if keywords:
            return ' '.join(keywords[:3]).title()
        
        return "Generated Content"
    
    def _create_fallback_image(self, content_data: Dict[str, Any], style: str) -> str:
        """Simple fallback image"""
        
        print(f"🔄 [FALLBACK] Creating simple fallback image...")
        
        img = Image.new('RGB', self.poster_size, color='#3498DB')
        draw = ImageDraw.Draw(img)
        
        title = self._extract_smart_title(content_data)
        self._draw_text_centered(draw, title, (540, 540), 60, 'white')
        
        return self._save_image(img, f"{style}_fallback")
    
    def _save_image(self, img: Image.Image, prefix: str) -> str:
        """Image'i tmp klasörüne kaydet"""
        try:
            # tmp directory
            tmp_dir = os.path.join(os.path.dirname(__file__), "..", "tmp")
            os.makedirs(tmp_dir, exist_ok=True)
            
            # Unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            filename = f"{prefix}_{timestamp}_{unique_id}.png"
            filepath = os.path.join(tmp_dir, filename)
            
            # Save with high quality
            img.save(filepath, "PNG", quality=95, optimize=True)
            
            print(f"🖼️ [SAVE] Image saved: {filename}")
            print(f"📁 [SAVE] Location: {tmp_dir}")
            print(f"📏 [SAVE] Size: {img.size[0]}x{img.size[1]} pixels")
            
            logger.info(f"Image saved: {filename}")
            
            return filepath
            
        except Exception as e:
            print(f"❌ [SAVE] Save failed: {e}")
            logger.error(f"Failed to save image: {e}")
            raise

# Singleton
_simple_generator = None

def get_simple_image_generator() -> SimpleImageGenerator:
    global _simple_generator
    if _simple_generator is None:
        _simple_generator = SimpleImageGenerator()
    return _simple_generator
