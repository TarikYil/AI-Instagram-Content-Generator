import os
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging
from dotenv import load_dotenv

# PIL imports (always needed)
from PIL import Image, ImageDraw, ImageFont

# Stable Diffusion imports (optional)
try:
    from diffusers import StableDiffusionPipeline
    import torch
    DIFFUSION_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Stable Diffusion not available: {e}")
    StableDiffusionPipeline = None
    torch = None
    DIFFUSION_AVAILABLE = False

load_dotenv()
logger = logging.getLogger(__name__)

class StableDiffusionImageGenerator:
    def __init__(self):
        self.pipeline = None
        self.device = "cuda" if torch and torch.cuda.is_available() else "cpu"
        self.poster_size = (1080, 1080)  # Instagram square format
        self._setup_pipeline()
        
    def _setup_pipeline(self):
        """Stable Diffusion pipeline kurulumu - Detaylı debug"""
        print(f"\n🔧 [SETUP] Starting Stable Diffusion pipeline setup...")
        print(f"🔍 [SETUP] Diffusion available: {DIFFUSION_AVAILABLE}")
        print(f"🔍 [SETUP] Torch available: {torch is not None}")
        
        if not DIFFUSION_AVAILABLE:
            print("⚠️ [SETUP] Stable Diffusion not available, using fallback text generation")
            print("⚠️ [SETUP] Install: pip install diffusers transformers torch")
            return
            
        try:
            print("🚀 [SETUP] Loading Stable Diffusion pipeline...")
            
            # Device detection
            print(f"🔍 [SETUP] Detecting device...")
            if torch.cuda.is_available():
                print(f"✅ [SETUP] CUDA available: {torch.cuda.get_device_name()}")
                print(f"✅ [SETUP] CUDA memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
            else:
                print(f"⚠️ [SETUP] CUDA not available, using CPU")
            
            print(f"🔧 [SETUP] Selected device: {self.device}")
            
            # Model loading
            model_id = "sd-legacy/stable-diffusion-v1-5"
            print(f"📥 [SETUP] Loading model: {model_id}")
            print(f"📥 [SETUP] This may take several minutes on first run...")
            
            # Pipeline configuration
            pipeline_config = {
                "torch_dtype": torch.float16 if self.device == "cuda" else torch.float32,
                "safety_checker": None,  # Hız için devre dışı
                "requires_safety_checker": False,
                "use_safetensors": True  # Safer format
            }
            
            print(f"⚙️ [SETUP] Pipeline config:")
            for key, value in pipeline_config.items():
                print(f"   • {key}: {value}")
            
            # Load pipeline
            import time
            load_start = time.time()
            
            self.pipeline = StableDiffusionPipeline.from_pretrained(
                model_id,
                **pipeline_config
            )
            
            load_time = time.time() - load_start
            print(f"📥 [SETUP] Model loaded in {load_time:.1f} seconds")
            
            # Move to device and optimize
            if self.device == "cuda":
                print(f"🚀 [SETUP] Moving pipeline to CUDA...")
                self.pipeline = self.pipeline.to("cuda")
                
                print(f"🔧 [SETUP] Enabling optimizations...")
                # Memory optimization
                self.pipeline.enable_attention_slicing()
                
                try:
                    self.pipeline.enable_memory_efficient_attention()
                    print(f"✅ [SETUP] Memory efficient attention enabled")
                except Exception as opt_e:
                    print(f"⚠️ [SETUP] Memory efficient attention failed: {opt_e}")
                
                # Check VRAM usage
                if torch.cuda.is_available():
                    memory_used = torch.cuda.memory_allocated() / 1e9
                    print(f"📊 [SETUP] CUDA memory used: {memory_used:.1f} GB")
            
            print(f"✅ [SETUP] Stable Diffusion pipeline ready on {self.device}")
            print(f"✅ [SETUP] Model components loaded:")
            print(f"   • UNet: {self.pipeline.unet is not None}")
            print(f"   • VAE: {self.pipeline.vae is not None}")
            print(f"   • Text Encoder: {self.pipeline.text_encoder is not None}")
            print(f"   • Tokenizer: {self.pipeline.tokenizer is not None}")
            print(f"   • Scheduler: {self.pipeline.scheduler is not None}")
            
            logger.info(f"Stable Diffusion pipeline loaded on {self.device}")
            
        except Exception as e:
            print(f"\n❌ [SETUP] Failed to load Stable Diffusion!")
            print(f"❌ [SETUP] Error: {str(e)}")
            print(f"❌ [SETUP] Error type: {type(e).__name__}")
            
            # Detailed error info
            import traceback
            print(f"❌ [SETUP] Traceback:")
            traceback.print_exc()
            
            logger.error(f"Stable Diffusion setup failed: {e}")
            self.pipeline = None
            
            print(f"🔄 [SETUP] Will use fallback text-based generation")
    
    def generate_instagram_image(self, 
                                content_data: Dict[str, Any],
                                trend_data: Optional[Dict[str, Any]] = None,
                                style: str = "modern") -> str:
        """
        Stable Diffusion ile Instagram image üret - Detaylı süreç takibi
        Returns: saved image file path
        """
        try:
            print(f"\n🚀 [MAIN] Starting Instagram image generation...")
            print(f"🎨 [MAIN] Style: {style}")
            print(f"📊 [MAIN] Pipeline available: {self.pipeline is not None}")
            print(f"🔧 [MAIN] Device: {self.device}")
            
            # Input data debug
            print(f"\n📋 [INPUT] Content Data:")
            print(f"   • Visual Summary: {content_data.get('visual_summary', 'N/A')}")
            print(f"   • Keywords: {content_data.get('keywords', [])}")
            print(f"   • Hashtags: {content_data.get('hashtags', [])}")
            
            if trend_data:
                print(f"📈 [INPUT] Trend Data:")
                print(f"   • Trends: {trend_data.get('trends', [])}")
                print(f"   • Trend Hashtags: {trend_data.get('hashtags', [])}")
            else:
                print(f"📈 [INPUT] No trend data provided")
            
            # Prompt oluştur
            print(f"\n🔄 [PROMPT] Creating enhanced prompt...")
            prompt = self._create_prompt(content_data, trend_data, style)
            print(f"📝 [PROMPT] Final prompt length: {len(prompt)} characters")
            
            if self.pipeline:
                print(f"\n🤖 [PIPELINE] Using Stable Diffusion pipeline...")
                
                # Stable Diffusion ile görsel üret
                print(f"🎨 [GENERATION] Starting Stable Diffusion generation...")
                image = self._generate_with_diffusion(prompt)
                
                print(f"✅ [GENERATION] Raw image generated: {image.size}")
                
                # Instagram formatına dönüştür
                print(f"📱 [FORMAT] Converting to Instagram format...")
                instagram_image = self._format_for_instagram(image, content_data, style)
                print(f"✅ [FORMAT] Instagram format ready: {instagram_image.size}")
                
            else:
                print(f"⚠️ [FALLBACK] Pipeline not available, using text-based poster...")
                # Fallback: Text-based poster
                instagram_image = self._create_text_poster(content_data, style)
            
            # Kaydet ve döndür
            print(f"💾 [SAVE] Saving image to tmp directory...")
            saved_path = self._save_image(instagram_image, f"{style}_instagram")
            
            print(f"🎉 [SUCCESS] Instagram image generation completed!")
            print(f"📁 [SUCCESS] Saved to: {saved_path}")
            
            return saved_path
            
        except Exception as e:
            print(f"\n❌ [ERROR] Image generation failed!")
            print(f"❌ [ERROR] Error: {str(e)}")
            print(f"❌ [ERROR] Error type: {type(e).__name__}")
            
            logger.error(f"Image generation failed: {e}")
            
            print(f"🔄 [FALLBACK] Creating fallback image...")
            return self._create_fallback_image(content_data, style)
    
    def _create_prompt(self, content_data: Dict[str, Any], 
                      trend_data: Optional[Dict[str, Any]], 
                      style: str) -> str:
        """Diğer servislerden gelen bilgilerle Stable Diffusion prompt oluştur"""
        
        # Analysis servisinden gelen bilgiler
        visual_summary = content_data.get('visual_summary', 'amazing content')
        video_summary = content_data.get('video_summary', '')
        keywords = content_data.get('keywords', [])
        hashtags = content_data.get('hashtags', [])
        
        # Trend servisinden gelen bilgiler
        trends = []
        trend_hashtags = []
        if trend_data:
            trends = trend_data.get('trends', [])
            trend_hashtags = trend_data.get('hashtags', [])
        
        print(f"🔍 [PROMPT] Visual Summary: {visual_summary}")
        print(f"🔍 [PROMPT] Keywords: {keywords}")
        print(f"🔍 [PROMPT] Trends: {trends}")
        print(f"🔍 [PROMPT] Style: {style}")
        
        # Style'a göre görsel tarzı
        style_prompts = {
            "modern": "modern minimalist design, clean aesthetics, professional layout, sleek interface,",
            "gaming": "gaming aesthetic, neon colors, futuristic design, cyberpunk style, digital art, vibrant lighting,",
            "minimal": "minimal design, white background, clean typography, simple layout, geometric shapes,",
            "trendy": "trendy social media design, vibrant colors, instagram style, modern graphics, gradient backgrounds,"
        }
        
        style_prefix = style_prompts.get(style, style_prompts["modern"])
        
        # Ana içerik analizi
        main_visual_elements = self._extract_visual_elements(visual_summary, video_summary)
        
        # Keyword'lerden görsel öğeler çıkar
        visual_keywords = self._filter_visual_keywords(keywords)
        
        # Trend'lerden görsel trendler
        visual_trends = self._extract_visual_trends(trends)
        
        # Color scheme çıkar
        color_scheme = self._determine_color_scheme(keywords, trends, style)
        
        # Composition elements
        composition = self._determine_composition(style, keywords)
        
        # Final prompt oluştur
        prompt_parts = [
            style_prefix,
            main_visual_elements,
            f"featuring {', '.join(visual_keywords[:4])}" if visual_keywords else "",
            f"with {color_scheme} color scheme",
            composition,
            f"trending style: {', '.join(visual_trends[:2])}" if visual_trends else "",
            "high quality, detailed, professional, social media ready, instagram post, digital art, 4k resolution, sharp focus"
        ]
        
        # Boş parçaları filtrele
        prompt_parts = [part for part in prompt_parts if part.strip()]
        
        final_prompt = ", ".join(prompt_parts)
        
        print(f"✨ [PROMPT] Generated: {final_prompt[:100]}...")
        
        return final_prompt
    
    def _extract_visual_elements(self, visual_summary: str, video_summary: str) -> str:
        """Görsel öğeleri analiz et"""
        
        combined_text = f"{visual_summary} {video_summary}".lower()
        
        # Görsel öğeler sözlüğü
        visual_mapping = {
            'mobile': 'smartphone interface, mobile app design',
            'game': 'game interface, interactive elements, game graphics',
            'puzzle': 'puzzle pieces, geometric patterns, brain teaser elements',
            'colorful': 'vibrant colors, rainbow palette, bright hues',
            'dark': 'dark theme, shadows, moody lighting',
            'bright': 'bright lighting, illuminated, glowing effects',
            'modern': 'contemporary design, sleek elements',
            'retro': 'vintage style, retro aesthetics',
            'nature': 'natural elements, organic shapes',
            'technology': 'tech elements, digital interface, futuristic'
        }
        
        detected_elements = []
        for keyword, visual_desc in visual_mapping.items():
            if keyword in combined_text:
                detected_elements.append(visual_desc)
        
        if detected_elements:
            return f"showing {', '.join(detected_elements[:3])}"
        else:
            return f"displaying {visual_summary[:50]}"
    
    def _filter_visual_keywords(self, keywords: List[str]) -> List[str]:
        """Görsel açıdan anlamlı keyword'leri filtrele"""
        
        visual_keywords = []
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            # Görsel keyword'ler
            if any(visual_term in keyword_lower for visual_term in [
                'color', 'bright', 'dark', 'neon', 'glow', 'shine',
                'game', 'app', 'interface', 'design', 'art',
                'mobile', 'digital', 'tech', 'modern', 'retro',
                'puzzle', 'pattern', 'shape', 'geometric'
            ]):
                visual_keywords.append(keyword)
            elif len(keyword) > 3:  # Genel keyword'ler
                visual_keywords.append(keyword)
        
        return visual_keywords[:5]
    
    def _extract_visual_trends(self, trends: List[str]) -> List[str]:
        """Trend'lerden görsel trendleri çıkar"""
        
        visual_trends = []
        for trend in trends:
            trend_lower = trend.lower()
            
            # Görsel trend mapping
            if 'gaming' in trend_lower:
                visual_trends.append('gaming aesthetics')
            elif 'mobile' in trend_lower:
                visual_trends.append('mobile design')
            elif 'retro' in trend_lower:
                visual_trends.append('retro style')
            elif 'neon' in trend_lower:
                visual_trends.append('neon effects')
            elif 'minimal' in trend_lower:
                visual_trends.append('minimalist design')
            else:
                visual_trends.append(f"{trend} style")
        
        return visual_trends[:3]
    
    def _determine_color_scheme(self, keywords: List[str], trends: List[str], style: str) -> str:
        """Keyword ve trend'lere göre renk şeması belirle"""
        
        all_terms = ' '.join(keywords + trends + [style]).lower()
        
        # Renk şeması mapping
        if any(term in all_terms for term in ['gaming', 'neon', 'cyber']):
            return "neon blue and pink"
        elif any(term in all_terms for term in ['nature', 'green', 'organic']):
            return "natural green and earth tones"
        elif any(term in all_terms for term in ['minimal', 'clean', 'white']):
            return "monochromatic white and gray"
        elif any(term in all_terms for term in ['warm', 'orange', 'sunset']):
            return "warm orange and yellow"
        elif any(term in all_terms for term in ['cool', 'blue', 'ocean']):
            return "cool blue and teal"
        elif any(term in all_terms for term in ['dark', 'black', 'shadow']):
            return "dark theme with accent colors"
        elif any(term in all_terms for term in ['colorful', 'rainbow', 'vibrant']):
            return "vibrant multicolor"
        else:
            # Style'a göre default
            style_colors = {
                'gaming': 'neon blue and purple',
                'modern': 'blue and white',
                'minimal': 'grayscale with blue accent',
                'trendy': 'gradient pink and orange'
            }
            return style_colors.get(style, 'balanced color palette')
    
    def _determine_composition(self, style: str, keywords: List[str]) -> str:
        """Kompozisyon öğelerini belirle"""
        
        keywords_text = ' '.join(keywords).lower()
        
        compositions = {
            'gaming': 'dynamic composition, action-oriented layout, gaming UI elements',
            'modern': 'centered composition, balanced layout, professional spacing',
            'minimal': 'simple composition, lots of white space, clean alignment',
            'trendy': 'creative composition, asymmetric layout, modern elements'
        }
        
        base_composition = compositions.get(style, compositions['modern'])
        
        # Keyword'lere göre ek kompozisyon
        if 'mobile' in keywords_text:
            base_composition += ', mobile interface elements'
        if 'puzzle' in keywords_text:
            base_composition += ', puzzle game layout'
        
        return base_composition
    
    def _generate_with_diffusion(self, prompt: str) -> Image.Image:
        """Stable Diffusion ile görsel üret - Detaylı debug ile"""
        
        try:
            print(f"\n🎨 [DIFFUSION] Starting Stable Diffusion generation...")
            print(f"🔧 [DIFFUSION] Device: {self.device}")
            print(f"🤖 [DIFFUSION] Model: sd-legacy/stable-diffusion-v1-5")
            print(f"📝 [DIFFUSION] Full Prompt: {prompt}")
            
            # Generation parameters
            generation_params = {
                "prompt": prompt,
                "height": 512,  # Stable Diffusion optimal size
                "width": 512,
                "num_inference_steps": 25,  # Biraz artırdık kalite için
                "guidance_scale": 7.5,
                "num_images_per_prompt": 1,
                "negative_prompt": "blurry, low quality, distorted, text, watermark, signature, ugly, bad anatomy, extra limbs, deformed"
            }
            
            print(f"⚙️ [DIFFUSION] Generation Parameters:")
            for key, value in generation_params.items():
                print(f"   • {key}: {value}")
            
            print(f"\n⏳ [DIFFUSION] Starting inference ({generation_params['num_inference_steps']} steps)...")
            
            # Progress tracking için callback function
            def progress_callback(step, timestep, latents):
                progress = (step + 1) / generation_params['num_inference_steps'] * 100
                print(f"   Step {step + 1}/{generation_params['num_inference_steps']} ({progress:.1f}%) - Timestep: {timestep}")
            
            # Generate image with progress tracking
            import time
            start_time = time.time()
            
            if self.device == "cuda" and torch.cuda.is_available():
                print(f"🚀 [DIFFUSION] Using CUDA acceleration...")
                with torch.autocast("cuda"):
                    result = self.pipeline(
                        **generation_params,
                        callback=progress_callback,
                        callback_steps=5  # Her 5 step'de progress göster
                    )
            else:
                print(f"🐌 [DIFFUSION] Using CPU (slower)...")
                result = self.pipeline(
                    **generation_params,
                    callback=progress_callback,
                    callback_steps=5
                )
            
            generation_time = time.time() - start_time
            image = result.images[0]
            
            print(f"\n✅ [DIFFUSION] Generation completed successfully!")
            print(f"⏱️ [DIFFUSION] Generation time: {generation_time:.2f} seconds")
            print(f"📏 [DIFFUSION] Generated image size: {image.size}")
            print(f"🎨 [DIFFUSION] Image mode: {image.mode}")
            
            # Image quality check
            if hasattr(result, 'nsfw_content_detected'):
                print(f"🔍 [DIFFUSION] NSFW check: {result.nsfw_content_detected}")
            
            return image
            
        except Exception as e:
            print(f"\n❌ [DIFFUSION] Generation failed!")
            print(f"❌ [DIFFUSION] Error: {str(e)}")
            print(f"❌ [DIFFUSION] Error type: {type(e).__name__}")
            
            # Detailed error info
            import traceback
            print(f"❌ [DIFFUSION] Traceback:")
            traceback.print_exc()
            
            raise
    
    def _format_for_instagram(self, base_image: Image.Image, 
                             content_data: Dict[str, Any], 
                             style: str) -> Image.Image:
        """Üretilen görseli Instagram formatına dönüştür"""
        
        # Instagram square format (1080x1080)
        instagram_img = Image.new('RGB', self.poster_size, color='white')
        
        # Base image'i resize et ve merkeze yerleştir
        base_image = base_image.resize((800, 800), Image.Resampling.LANCZOS)
        
        # Merkeze yerleştir
        x = (self.poster_size[0] - 800) // 2
        y = (self.poster_size[1] - 800) // 2 - 50  # Biraz yukarı kaydır
        
        instagram_img.paste(base_image, (x, y))
        
        # Text overlay ekle
        draw = ImageDraw.Draw(instagram_img)
        
        # Title
        title = self._extract_title(content_data)
        self._draw_text_overlay(draw, title, (540, 950), 48, 'black', center=True)
        
        # Keywords
        keywords = content_data.get('keywords', [])
        if keywords:
            keywords_text = " • ".join(keywords[:4])
            self._draw_text_overlay(draw, keywords_text, (540, 1000), 32, 'gray', center=True)
        
        return instagram_img
    
    def _create_text_poster(self, content_data: Dict[str, Any], style: str) -> Image.Image:
        """Fallback: Text-based poster oluştur"""
        
        # Style'a göre renkler
        colors = {
            "modern": {"bg": "#2C3E50", "primary": "#3498DB", "text": "#FFFFFF"},
            "gaming": {"bg": "#0D1117", "primary": "#FF0080", "text": "#00D9FF"},
            "minimal": {"bg": "#F8F9FA", "primary": "#2C3E50", "text": "#2C3E50"},
            "trendy": {"bg": "#FF6B6B", "primary": "#FFFFFF", "text": "#2C3E50"}
        }
        
        style_colors = colors.get(style, colors["modern"])
        
        # Create image
        img = Image.new('RGB', self.poster_size, color=style_colors["bg"])
        draw = ImageDraw.Draw(img)
        
        # Title
        title = self._extract_title(content_data)
        self._draw_text_overlay(draw, title, (540, 300), 64, style_colors["primary"], center=True)
        
        # Visual summary
        visual_summary = content_data.get('visual_summary', 'Amazing content!')
        self._draw_wrapped_text(draw, visual_summary, (100, 450), 36, style_colors["text"], 880)
        
        # Keywords as badges
        keywords = content_data.get('keywords', [])
        if keywords:
            self._draw_keyword_badges(draw, keywords[:6], (540, 700), style_colors)
        
        # Branding
        self._draw_text_overlay(draw, "AI Generated Content", (540, 1000), 24, style_colors["text"], center=True)
        
        return img
    
    def _create_fallback_image(self, content_data: Dict[str, Any], style: str) -> str:
        """Ultra simple fallback"""
        
        img = Image.new('RGB', self.poster_size, color='#3498DB')
        draw = ImageDraw.Draw(img)
        
        # Simple text
        title = self._extract_title(content_data)
        self._draw_text_overlay(draw, title, (540, 540), 72, 'white', center=True)
        
        return self._save_image(img, "fallback_image")
    
    def _extract_title(self, content_data: Dict[str, Any]) -> str:
        """İçerikten başlık çıkar"""
        
        visual_summary = content_data.get('visual_summary', '')
        keywords = content_data.get('keywords', [])
        
        if visual_summary:
            words = visual_summary.split()[:4]
            if len(words) >= 2:
                return ' '.join(words).title()
        
        if keywords:
            return ' '.join(keywords[:3]).title()
        
        return "Generated Content"
    
    def _draw_text_overlay(self, draw, text: str, position: tuple, size: int, color: str, center: bool = False):
        """Text çiz"""
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
            draw.text(position, text[:50], fill=color)
    
    def _draw_wrapped_text(self, draw, text: str, position: tuple, size: int, color: str, max_width: int):
        """Wrapped text çiz"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
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
        
        for line in lines[:5]:  # Max 5 lines
            self._draw_text_overlay(draw, line, (position[0], position[1] + y_offset), size, color)
            y_offset += line_height
    
    def _draw_keyword_badges(self, draw, keywords: List[str], position: tuple, colors: dict):
        """Keyword badge'leri çiz"""
        x, y = position
        
        for i, keyword in enumerate(keywords[:4]):
            col = i % 2
            row = i // 2
            
            badge_x = x - 200 + col * 400
            badge_y = y + row * 80
            
            # Badge background
            draw.rectangle([(badge_x-100, badge_y-25), (badge_x+100, badge_y+25)], 
                         fill=colors["primary"], outline=colors["text"], width=2)
            
            # Badge text
            self._draw_text_overlay(draw, f"#{keyword}", (badge_x, badge_y), 20, colors["bg"], center=True)
    
    def _save_image(self, img: Image.Image, prefix: str) -> str:
        """Image'i tmp klasörüne kaydet"""
        try:
            # Create tmp directory if not exists
            tmp_dir = os.path.join(os.path.dirname(__file__), "..", "tmp")
            os.makedirs(tmp_dir, exist_ok=True)
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            filename = f"{prefix}_{timestamp}_{unique_id}.png"
            filepath = os.path.join(tmp_dir, filename)
            
            # Save with high quality
            img.save(filepath, "PNG", quality=95, optimize=True)
            
            print(f"🖼️ [STABLE DIFFUSION] Image saved: {filename}")
            print(f"📁 [LOCATION] {tmp_dir}")
            print(f"📏 [SIZE] {img.size[0]}x{img.size[1]} pixels")
            logger.info(f"Stable Diffusion image saved: {filename}")
            
            return filepath
            
        except Exception as e:
            print(f"❌ [SAVE ERROR] Failed to save image: {e}")
            logger.error(f"Failed to save image: {e}")
            raise

# Singleton instance
_sd_generator = None

def get_stable_diffusion_generator() -> StableDiffusionImageGenerator:
    global _sd_generator
    if _sd_generator is None:
        _sd_generator = StableDiffusionImageGenerator()
    return _sd_generator
