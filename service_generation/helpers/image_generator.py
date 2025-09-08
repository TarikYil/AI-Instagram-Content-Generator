import os
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import logging
from dotenv import load_dotenv

# Optional matplotlib import (not required for basic poster generation)
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    MATPLOTLIB_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Matplotlib not available (optional): {e}")
    plt = None
    patches = None
    MATPLOTLIB_AVAILABLE = False

# Optional Gemini import for AI-powered image descriptions
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Gemini API not available for image generation: {e}")
    genai = None
    GEMINI_AVAILABLE = False

load_dotenv()

logger = logging.getLogger(__name__)

class InstagramPosterGenerator:
    def __init__(self):
        self.poster_size = (1080, 1080)  # Instagram square format
        self.story_size = (1080, 1920)   # Instagram story format
        self.gemini_client = None
        self._setup_gemini_client()
        
    def _setup_gemini_client(self):
        """Gemini AI client kurulumu"""
        if GEMINI_AVAILABLE:
            try:
                gemini_key = os.getenv("GEMINI_API_KEY")
                if gemini_key:
                    genai.configure(api_key=gemini_key)
                    # Gemini 2.5 Pro modelini kullan
                    self.gemini_client = genai.GenerativeModel('gemini-2.5-pro')
                    print("✅ Gemini 2.5 Pro client kuruldu (Image Generation)")
                    logger.info("✅ Gemini 2.5 Pro client setup for image generation")
                else:
                    logger.warning("⚠️ GEMINI_API_KEY bulunamadı")
            except Exception as e:
                logger.warning(f"⚠️ Gemini client kurulamadı: {e}")
        else:
            logger.warning("⚠️ Gemini API kütüphanesi mevcut değil")
        
    def create_instagram_poster(self, 
                              content_data: Dict[str, Any],
                              trend_data: Optional[Dict[str, Any]] = None,
                              style: str = "modern") -> str:
        """
        Instagram poster oluştur - Gemini 2.5 Pro ile enhanced
        Returns: saved image file path
        """
        try:
            # Gemini ile content'i enhance et
            enhanced_content = self._enhance_content_with_gemini(content_data, trend_data, style)
            
            # Enhanced content ile poster oluştur
            if style == "gaming":
                return self._create_gaming_poster(enhanced_content, trend_data)
            elif style == "minimal":
                return self._create_minimal_poster(enhanced_content, trend_data)
            elif style == "trendy":
                return self._create_trendy_poster(enhanced_content, trend_data)
            else:
                return self._create_modern_poster(enhanced_content, trend_data)
                
        except Exception as e:
            logger.error(f"Poster creation failed: {e}")
            return self._create_fallback_poster(content_data)
    
    def _enhance_content_with_gemini(self, content_data: Dict[str, Any], 
                                   trend_data: Optional[Dict[str, Any]], 
                                   style: str) -> Dict[str, Any]:
        """Gemini 2.5 Pro ile content'i enhance et"""
        
        if not self.gemini_client:
            print("⚠️ [GEMINI] Client not available, using original content")
            return content_data
        
        try:
            print(f"🤖 [GEMINI] Enhancing content with Gemini 2.5 Pro...")
            
            # Gemini için prompt oluştur
            prompt = self._create_enhancement_prompt(content_data, trend_data, style)
            
            # Gemini'den enhanced content al
            response = self.gemini_client.generate_content(prompt)
            enhanced_text = response.text
            
            print(f"✅ [GEMINI] Content enhanced successfully")
            logger.info("Content enhanced with Gemini 2.5 Pro")
            
            # Enhanced content'i parse et
            enhanced_content = self._parse_gemini_response(enhanced_text, content_data)
            
            return enhanced_content
            
        except Exception as e:
            print(f"⚠️ [GEMINI] Enhancement failed: {e}")
            logger.warning(f"Gemini enhancement failed: {e}")
            return content_data  # Fallback to original
    
    def _create_enhancement_prompt(self, content_data: Dict[str, Any], 
                                 trend_data: Optional[Dict[str, Any]], 
                                 style: str) -> str:
        """Gemini için enhancement prompt oluştur"""
        
        visual_summary = content_data.get('visual_summary', '')
        keywords = content_data.get('keywords', [])
        hashtags = content_data.get('hashtags', [])
        trends = trend_data.get('trends', []) if trend_data else []
        
        prompt = f"""
Sen bir Instagram poster tasarım uzmanısın. Aşağıdaki içerik verilerini kullanarak {style} stilinde bir Instagram poster için optimize edilmiş içerik oluştur.

MEVCUT İÇERİK:
- Görsel Özet: {visual_summary}
- Anahtar Kelimeler: {', '.join(keywords)}
- Hashtag'ler: {', '.join(hashtags)}
- Trendler: {', '.join(trends)}

POSTER STILI: {style}

Lütfen aşağıdaki formatı kullanarak optimize edilmiş içerik oluştur:

TITLE: [Çekici ve kısa bir başlık]
MAIN_TEXT: [Ana metin - poster için uygun uzunlukta]
HIGHLIGHT_KEYWORDS: [En önemli 4-5 anahtar kelime]
CALL_TO_ACTION: [Etkili bir çağrı]
ENHANCED_HASHTAGS: [En etkili 8-10 hashtag]
DESIGN_SUGGESTIONS: [Renk ve tasarım önerileri]

Türkçe yanıtla ve Instagram'da viral olabilecek, görsel olarak çekici içerik oluştur.
"""
        
        return prompt
    
    def _parse_gemini_response(self, response_text: str, original_content: Dict[str, Any]) -> Dict[str, Any]:
        """Gemini yanıtını parse et"""
        
        try:
            enhanced_content = original_content.copy()
            
            lines = response_text.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                
                if line.startswith('TITLE:'):
                    enhanced_content['title'] = line.replace('TITLE:', '').strip()
                elif line.startswith('MAIN_TEXT:'):
                    enhanced_content['visual_summary'] = line.replace('MAIN_TEXT:', '').strip()
                elif line.startswith('HIGHLIGHT_KEYWORDS:'):
                    keywords_text = line.replace('HIGHLIGHT_KEYWORDS:', '').strip()
                    enhanced_content['keywords'] = [k.strip() for k in keywords_text.split(',')]
                elif line.startswith('CALL_TO_ACTION:'):
                    enhanced_content['call_to_action'] = line.replace('CALL_TO_ACTION:', '').strip()
                elif line.startswith('ENHANCED_HASHTAGS:'):
                    hashtags_text = line.replace('ENHANCED_HASHTAGS:', '').strip()
                    enhanced_content['hashtags'] = [h.strip().replace('#', '') for h in hashtags_text.split()]
                elif line.startswith('DESIGN_SUGGESTIONS:'):
                    enhanced_content['design_suggestions'] = line.replace('DESIGN_SUGGESTIONS:', '').strip()
            
            print(f"✅ [GEMINI] Content parsed successfully")
            return enhanced_content
            
        except Exception as e:
            print(f"⚠️ [GEMINI] Parse error: {e}")
            return original_content
    
    def _create_modern_poster(self, content_data: Dict[str, Any], trend_data: Optional[Dict[str, Any]]) -> str:
        """Modern style Instagram poster"""
        
        # Create image
        img = Image.new('RGB', self.poster_size, color='#1a1a1a')  # Dark background
        draw = ImageDraw.Draw(img)
        
        try:
            # Font sizes (fallback to default if custom fonts not available)
            title_font_size = 72
            subtitle_font_size = 48
            text_font_size = 36
            
            # Colors
            primary_color = '#FF6B6B'    # Coral red
            secondary_color = '#4ECDC4'  # Teal
            text_color = '#FFFFFF'       # White
            accent_color = '#FFE66D'     # Yellow
            
            # Title area
            title = self._extract_title(content_data)
            self._draw_text_with_background(draw, title, (540, 200), title_font_size, 
                                          text_color, primary_color, center=True)
            
            # Visual summary
            visual_summary = content_data.get('visual_summary', 'Amazing content!')
            self._draw_wrapped_text(draw, visual_summary, (100, 350), 
                                  text_font_size, text_color, max_width=880)
            
            # Keywords section
            keywords = content_data.get('keywords', [])
            if keywords:
                self._draw_keywords_section(draw, keywords[:6], (100, 550), 
                                          secondary_color, text_color)
            
            # Trend info
            if trend_data and trend_data.get('trends'):
                trends = trend_data['trends'][:3]
                self._draw_trends_section(draw, trends, (100, 750), 
                                        accent_color, text_color)
            
            # Bottom branding
            self._draw_branding(draw, (540, 950), text_color)
            
            # Decorative elements
            self._add_decorative_elements(draw, primary_color, secondary_color)
            
        except Exception as e:
            logger.warning(f"Advanced poster creation failed, using simple version: {e}")
            # Simple fallback
            draw.rectangle([(50, 50), (1030, 1030)], outline=primary_color, width=5)
            self._draw_simple_text(draw, title, (540, 540), 60, text_color, center=True)
        
        # Save image
        return self._save_image(img, "modern_poster")
    
    def _create_gaming_poster(self, content_data: Dict[str, Any], trend_data: Optional[Dict[str, Any]]) -> str:
        """Gaming style Instagram poster"""
        
        # Gaming color scheme
        img = Image.new('RGB', self.poster_size, color='#0D1117')  # Dark GitHub-like
        draw = ImageDraw.Draw(img)
        
        gaming_colors = {
            'primary': '#FF0080',     # Hot pink
            'secondary': '#00D9FF',   # Cyan
            'accent': '#FFFF00',      # Yellow
            'text': '#FFFFFF'         # White
        }
        
        try:
            title = self._extract_title(content_data, default="🎮 GAMING CONTENT")
            
            # Gaming header
            self._draw_gaming_header(draw, title, gaming_colors)
            
            # Game features
            visual_summary = content_data.get('visual_summary', 'Epic gaming experience!')
            self._draw_gaming_features(draw, visual_summary, content_data.get('keywords', []), gaming_colors)
            
            # Gaming footer with hashtags
            hashtags = content_data.get('hashtags', ['#gaming', '#mobile', '#fun'])
            self._draw_gaming_footer(draw, hashtags, gaming_colors)
            
        except Exception as e:
            logger.warning(f"Gaming poster creation failed: {e}")
            self._draw_simple_text(draw, "🎮 GAMING", (540, 540), 80, gaming_colors['primary'], center=True)
        
        return self._save_image(img, "gaming_poster")
    
    def _create_minimal_poster(self, content_data: Dict[str, Any], trend_data: Optional[Dict[str, Any]]) -> str:
        """Minimal style Instagram poster"""
        
        # Minimal color scheme
        img = Image.new('RGB', self.poster_size, color='#F8F9FA')  # Light gray
        draw = ImageDraw.Draw(img)
        
        minimal_colors = {
            'primary': '#2C3E50',     # Dark blue-gray
            'secondary': '#3498DB',   # Blue
            'accent': '#E74C3C',      # Red
            'text': '#2C3E50',        # Dark text
            'light': '#BDC3C7'        # Light gray
        }
        
        try:
            title = self._extract_title(content_data, default="Quality Content")
            
            # Minimal header
            draw.line([(100, 150), (980, 150)], fill=minimal_colors['primary'], width=3)
            self._draw_simple_text(draw, title, (540, 250), 64, minimal_colors['primary'], center=True)
            
            # Content area
            visual_summary = content_data.get('visual_summary', 'Clean and professional content')
            self._draw_wrapped_text(draw, visual_summary, (150, 400), 
                                  42, minimal_colors['text'], max_width=780)
            
            # Minimal keywords
            keywords = content_data.get('keywords', [])[:4]
            if keywords:
                y_pos = 650
                for i, keyword in enumerate(keywords):
                    x_pos = 200 + (i * 170)
                    draw.rectangle([(x_pos-10, y_pos-10), (x_pos+150, y_pos+40)], 
                                 outline=minimal_colors['secondary'], width=2)
                    self._draw_simple_text(draw, keyword, (x_pos+70, y_pos+15), 24, 
                                         minimal_colors['secondary'], center=True)
            
            # Bottom line
            draw.line([(100, 900), (980, 900)], fill=minimal_colors['primary'], width=3)
            
        except Exception as e:
            logger.warning(f"Minimal poster creation failed: {e}")
            self._draw_simple_text(draw, title, (540, 540), 60, minimal_colors['primary'], center=True)
        
        return self._save_image(img, "minimal_poster")
    
    def _create_trendy_poster(self, content_data: Dict[str, Any], trend_data: Optional[Dict[str, Any]]) -> str:
        """Trendy style Instagram poster"""
        
        # Trendy gradient background
        img = Image.new('RGB', self.poster_size, color='#FF6B6B')
        draw = ImageDraw.Draw(img)
        
        # Create gradient effect (simple version)
        for y in range(self.poster_size[1]):
            ratio = y / self.poster_size[1]
            r = int(255 * (1 - ratio) + 107 * ratio)  # 255 to 107
            g = int(107 * (1 - ratio) + 185 * ratio)  # 107 to 185
            b = int(107 * (1 - ratio) + 240 * ratio)  # 107 to 240
            
            draw.line([(0, y), (self.poster_size[0], y)], fill=(r, g, b))
        
        trendy_colors = {
            'primary': '#FFFFFF',     # White
            'secondary': '#FFE66D',   # Yellow
            'accent': '#FF6B6B',      # Coral
            'text': '#2C3E50'         # Dark text
        }
        
        try:
            title = self._extract_title(content_data, default="🔥 TRENDING NOW")
            
            # Trendy header with emoji
            self._draw_text_with_shadow(draw, title, (540, 200), 68, 
                                      trendy_colors['primary'], (0, 0, 0, 50))
            
            # Trend indicators
            if trend_data and trend_data.get('trends'):
                trends = trend_data['trends'][:3]
                self._draw_trend_badges(draw, trends, (540, 350), trendy_colors)
            
            # Visual content
            visual_summary = content_data.get('visual_summary', 'Hot trending content!')
            self._draw_wrapped_text(draw, visual_summary, (100, 500), 
                                  40, trendy_colors['primary'], max_width=880)
            
            # Hashtag cloud
            hashtags = content_data.get('hashtags', [])
            if hashtags:
                self._draw_hashtag_cloud(draw, hashtags, (540, 750), trendy_colors)
            
        except Exception as e:
            logger.warning(f"Trendy poster creation failed: {e}")
            self._draw_simple_text(draw, "🔥 TRENDING", (540, 540), 80, 
                                 trendy_colors['primary'], center=True)
        
        return self._save_image(img, "trendy_poster")
    
    def _create_fallback_poster(self, content_data: Dict[str, Any]) -> str:
        """Simple fallback poster when advanced creation fails"""
        
        img = Image.new('RGB', self.poster_size, color='#2C3E50')
        draw = ImageDraw.Draw(img)
        
        # Simple design
        title = self._extract_title(content_data, default="Content Generated")
        
        # Border
        draw.rectangle([(50, 50), (1030, 1030)], outline='#3498DB', width=8)
        
        # Title
        self._draw_simple_text(draw, title, (540, 300), 60, '#FFFFFF', center=True)
        
        # Visual summary
        visual_summary = content_data.get('visual_summary', 'Generated content')
        self._draw_simple_text(draw, visual_summary[:50] + "...", (540, 500), 32, '#BDC3C7', center=True)
        
        # Simple branding
        self._draw_simple_text(draw, "AI Generated", (540, 800), 28, '#95A5A6', center=True)
        
        return self._save_image(img, "fallback_poster")
    
    # Helper methods
    def _extract_title(self, content_data: Dict[str, Any], default: str = "Generated Content") -> str:
        """Extract title from content data"""
        
        visual_summary = content_data.get('visual_summary', '')
        keywords = content_data.get('keywords', [])
        
        if visual_summary:
            # Take first meaningful part
            words = visual_summary.split()[:4]
            if len(words) >= 2:
                return ' '.join(words).title()
        
        if keywords:
            return ' '.join(keywords[:3]).title()
        
        return default
    
    def _draw_simple_text(self, draw, text: str, position: tuple, size: int, color: str, center: bool = False):
        """Draw simple text (fallback when custom fonts fail)"""
        try:
            if center:
                bbox = draw.textbbox((0, 0), text)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                x = position[0] - text_width // 2
                y = position[1] - text_height // 2
                draw.text((x, y), text, fill=color)
            else:
                draw.text(position, text, fill=color)
        except Exception:
            # Ultra-simple fallback
            draw.text(position, text[:30], fill=color)
    
    def _draw_wrapped_text(self, draw, text: str, position: tuple, size: int, color: str, max_width: int):
        """Draw wrapped text"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            try:
                bbox = draw.textbbox((0, 0), test_line)
                text_width = bbox[2] - bbox[0]
                
                if text_width <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        lines.append(word)
            except:
                # Simple fallback
                if len(test_line) * 12 <= max_width:  # Rough estimate
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw lines
        y_offset = 0
        line_height = size + 10
        
        for line in lines[:6]:  # Max 6 lines
            self._draw_simple_text(draw, line, (position[0], position[1] + y_offset), size, color)
            y_offset += line_height
    
    def _draw_text_with_background(self, draw, text: str, position: tuple, size: int, 
                                 text_color: str, bg_color: str, center: bool = False):
        """Draw text with background"""
        try:
            # Get text dimensions
            bbox = draw.textbbox((0, 0), text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            if center:
                x = position[0] - text_width // 2
                y = position[1] - text_height // 2
            else:
                x, y = position
            
            # Draw background rectangle
            padding = 20
            draw.rectangle([(x - padding, y - padding), 
                          (x + text_width + padding, y + text_height + padding)], 
                         fill=bg_color)
            
            # Draw text
            draw.text((x, y), text, fill=text_color)
            
        except Exception:
            # Fallback
            self._draw_simple_text(draw, text, position, size, text_color, center)
    
    def _draw_text_with_shadow(self, draw, text: str, position: tuple, size: int, 
                             text_color: str, shadow_color: tuple):
        """Draw text with shadow effect"""
        # Shadow
        shadow_pos = (position[0] + 3, position[1] + 3)
        self._draw_simple_text(draw, text, shadow_pos, size, shadow_color, center=True)
        
        # Main text
        self._draw_simple_text(draw, text, position, size, text_color, center=True)
    
    def _draw_keywords_section(self, draw, keywords: List[str], position: tuple, 
                             bg_color: str, text_color: str):
        """Draw keywords as badges"""
        x, y = position
        
        for i, keyword in enumerate(keywords):
            if i >= 6:  # Max 6 keywords
                break
                
            col = i % 3
            row = i // 3
            
            badge_x = x + col * 280
            badge_y = y + row * 80
            
            # Badge background
            draw.rounded_rectangle([(badge_x, badge_y), (badge_x + 250, badge_y + 60)], 
                                 radius=15, fill=bg_color)
            
            # Badge text
            self._draw_simple_text(draw, f"#{keyword}", (badge_x + 125, badge_y + 30), 
                                 24, text_color, center=True)
    
    def _draw_trends_section(self, draw, trends: List[str], position: tuple, 
                           accent_color: str, text_color: str):
        """Draw trending topics"""
        x, y = position
        
        # Section title
        self._draw_simple_text(draw, "🔥 TRENDING:", (x, y), 32, accent_color)
        
        # Trends
        for i, trend in enumerate(trends[:3]):
            trend_y = y + 50 + (i * 40)
            self._draw_simple_text(draw, f"• {trend}", (x + 20, trend_y), 28, text_color)
    
    def _draw_branding(self, draw, position: tuple, color: str):
        """Draw branding/watermark"""
        self._draw_simple_text(draw, "Generated by AI Content Creator", 
                             position, 24, color, center=True)
    
    def _add_decorative_elements(self, draw, primary_color: str, secondary_color: str):
        """Add decorative elements"""
        # Simple geometric shapes
        try:
            # Corner decorations
            draw.rectangle([(50, 50), (100, 100)], fill=primary_color)
            draw.rectangle([(980, 50), (1030, 100)], fill=secondary_color)
            draw.rectangle([(50, 980), (100, 1030)], fill=secondary_color)
            draw.rectangle([(980, 980), (1030, 1030)], fill=primary_color)
        except Exception:
            pass  # Skip decorations if they fail
    
    def _draw_gaming_header(self, draw, title: str, colors: dict):
        """Draw gaming style header"""
        # Gaming border effect
        for i in range(5):
            color = colors['primary'] if i % 2 == 0 else colors['secondary']
            draw.rectangle([(50 + i*5, 50 + i*5), (1030 - i*5, 200 - i*5)], 
                         outline=color, width=2)
        
        # Title
        self._draw_simple_text(draw, title, (540, 125), 56, colors['text'], center=True)
    
    def _draw_gaming_features(self, draw, visual_summary: str, keywords: List[str], colors: dict):
        """Draw gaming features section"""
        # Visual summary
        self._draw_wrapped_text(draw, visual_summary, (100, 250), 36, colors['text'], 880)
        
        # Gaming keywords as power-ups
        for i, keyword in enumerate(keywords[:4]):
            x = 150 + (i * 200)
            y = 450
            
            # Power-up box
            draw.rectangle([(x-50, y-30), (x+150, y+30)], fill=colors['accent'], outline=colors['primary'], width=3)
            self._draw_simple_text(draw, keyword.upper(), (x+50, y), 20, colors['primary'], center=True)
    
    def _draw_gaming_footer(self, draw, hashtags: List[str], colors: dict):
        """Draw gaming style footer"""
        # Footer background
        draw.rectangle([(50, 800), (1030, 950)], fill=colors['primary'], outline=colors['secondary'], width=3)
        
        # Hashtags
        hashtag_text = ' '.join(hashtags[:8])
        self._draw_wrapped_text(draw, hashtag_text, (100, 830), 28, colors['text'], 830)
    
    def _draw_trend_badges(self, draw, trends: List[str], position: tuple, colors: dict):
        """Draw trend badges"""
        x, y = position
        
        for i, trend in enumerate(trends):
            badge_x = x - 300 + (i * 200)
            
            # Badge
            draw.ellipse([(badge_x-80, y-30), (badge_x+80, y+30)], fill=colors['secondary'])
            self._draw_simple_text(draw, trend[:8], (badge_x, y), 20, colors['text'], center=True)
    
    def _draw_hashtag_cloud(self, draw, hashtags: List[str], position: tuple, colors: dict):
        """Draw hashtag cloud"""
        x, y = position
        
        # Random-ish positions for hashtags
        positions = [
            (x-200, y-50), (x+100, y-30), (x-50, y+20),
            (x+150, y+50), (x-150, y+80), (x+50, y+100)
        ]
        
        for i, hashtag in enumerate(hashtags[:6]):
            if i < len(positions):
                pos = positions[i]
                size = 24 + (i % 3) * 4  # Varying sizes
                self._draw_simple_text(draw, f"#{hashtag}", pos, size, colors['primary'])
    
    def _save_image(self, img: Image.Image, prefix: str) -> str:
        """Save image to tmp directory and return filepath"""
        try:
            # Create tmp directory if not exists
            tmp_dir = os.path.join(os.path.dirname(__file__), "..", "tmp")
            os.makedirs(tmp_dir, exist_ok=True)
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            filename = f"{prefix}_{timestamp}_{unique_id}.png"
            filepath = os.path.join(tmp_dir, filename)
            
            # Save image with high quality
            img.save(filepath, "PNG", quality=95, optimize=True)
            
            # Log the save operation
            print(f"🖼️ [IMAGE SAVED] {filename}")
            print(f"📁 [LOCATION] {tmp_dir}")
            print(f"📏 [SIZE] {img.size[0]}x{img.size[1]} pixels")
            logger.info(f"Instagram poster saved to tmp: {filename}")
            
            return filepath
            
        except Exception as e:
            print(f"❌ [SAVE ERROR] Failed to save image: {e}")
            logger.error(f"Failed to save image: {e}")
            raise

# Singleton instance
_image_generator = None

def get_image_generator() -> InstagramPosterGenerator:
    global _image_generator
    if _image_generator is None:
        _image_generator = InstagramPosterGenerator()
    return _image_generator
