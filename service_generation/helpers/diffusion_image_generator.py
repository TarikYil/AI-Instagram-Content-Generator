import os
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging
from dotenv import load_dotenv

# PIL import (always needed)
from PIL import Image

# Stable Diffusion imports (optional)
try:
    from diffusers import StableDiffusionPipeline
    import torch
    DIFFUSION_AVAILABLE = True
    print("✅ Stable Diffusion kütüphaneleri yüklendi")
except ImportError as e:
    print(f"❌ Stable Diffusion not available: {e}")
    StableDiffusionPipeline = None
    torch = None
    DIFFUSION_AVAILABLE = False

load_dotenv()
logger = logging.getLogger(__name__)

class DiffusionImageGenerator:
    def __init__(self):
        self.pipe = None
        self.device = "cuda" if (torch and torch.cuda.is_available()) else "cpu"
        self.poster_size = (1080, 1080)
        self._setup_pipeline()
        
    def _setup_pipeline(self):
        """Stable Diffusion pipeline kurulumu"""
        
        print(f"\n🔧 [SETUP] Stable Diffusion pipeline kuruluyor...")
        print(f"🔍 [SETUP] Diffusion available: {DIFFUSION_AVAILABLE}")
        
        if not DIFFUSION_AVAILABLE:
            print("❌ [SETUP] Stable Diffusion kütüphaneleri eksik!")
            print("💡 [SETUP] Yüklemek için: pip install diffusers torch transformers")
            return
            
        try:
            print(f"🔧 [SETUP] Device: {self.device}")
            
            if torch and torch.cuda.is_available():
                print(f"🚀 [SETUP] CUDA available: {torch.cuda.get_device_name()}")
                print(f"📊 [SETUP] CUDA memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
            else:
                print(f"⚠️ [SETUP] CUDA not available, using CPU (slower)")
            
            # Model yükleme
            model_id = "runwayml/stable-diffusion-v1-5"
            print(f"📥 [SETUP] Loading model: {model_id}")
            print(f"⏳ [SETUP] İlk yüklemede birkaç dakika sürebilir...")
            
            # Pipeline kurulum
            self.pipe = StableDiffusionPipeline.from_pretrained(
                model_id, 
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                safety_checker=None,
                requires_safety_checker=False
            )
            
            # Device'a taşı
            self.pipe = self.pipe.to(self.device)
            
            print(f"✅ [SETUP] Pipeline başarıyla kuruldu!")
            logger.info(f"Stable Diffusion pipeline ready on {self.device}")
            
        except Exception as e:
            print(f"❌ [SETUP] Pipeline kurulum hatası: {e}")
            logger.error(f"Pipeline setup failed: {e}")
            self.pipe = None
    
    def generate_instagram_image(self, 
                                content_data: Dict[str, Any],
                                trend_data: Optional[Dict[str, Any]] = None,
                                style: str = "modern") -> str:
        """
        Diğer servislerden gelen bilgilerle Instagram image üret
        """
        try:
            print(f"\n🎨 [GENERATION] Instagram image generation başlıyor...")
            print(f"🎨 [GENERATION] Style: {style}")
            print(f"🤖 [GENERATION] Pipeline ready: {self.pipe is not None}")
            
            # Input data debug
            print(f"\n📋 [INPUT] Content Data:")
            print(f"   • Visual Summary: {content_data.get('visual_summary', 'N/A')}")
            print(f"   • Keywords: {content_data.get('keywords', [])}")
            print(f"   • Hashtags: {content_data.get('hashtags', [])}")
            
            if trend_data:
                print(f"📈 [INPUT] Trend Data:")
                print(f"   • Trends: {trend_data.get('trends', [])}")
            
            # Prompt oluştur
            prompt = self._create_prompt_from_services(content_data, trend_data, style)
            
            if self.pipe:
                print(f"\n🤖 [AI] Stable Diffusion ile görsel üretiliyor...")
                print(f"📝 [AI] Prompt: {prompt}")
                
                # Stable Diffusion ile üret
                image = self._generate_with_stable_diffusion(prompt)
                
                # Instagram formatına dönüştür
                instagram_image = self._resize_for_instagram(image)
                
            else:
                print(f"⚠️ [FALLBACK] Pipeline yok, fallback image oluşturuluyor...")
                instagram_image = self._create_fallback_image(content_data, style)
            
            # Kaydet
            saved_path = self._save_image(instagram_image, f"{style}_generated")
            
            print(f"🎉 [SUCCESS] Generation tamamlandı: {saved_path}")
            return saved_path
            
        except Exception as e:
            print(f"❌ [ERROR] Generation başarısız: {e}")
            logger.error(f"Image generation failed: {e}")
            return self._create_fallback_image(content_data, style)
    
    def _create_prompt_from_services(self, content_data: Dict[str, Any], 
                                   trend_data: Optional[Dict[str, Any]], 
                                   style: str) -> str:
        """Diğer servislerden gelen bilgilere göre prompt oluştur"""
        
        print(f"\n🔄 [PROMPT] Servis bilgilerinden prompt oluşturuluyor...")
        
        # Analysis servisinden gelen bilgiler
        visual_summary = content_data.get('visual_summary', 'amazing content')
        keywords = content_data.get('keywords', [])
        hashtags = content_data.get('hashtags', [])
        
        print(f"📊 [PROMPT] Visual summary: {visual_summary}")
        print(f"📊 [PROMPT] Keywords: {keywords}")
        
        # Trend servisinden gelen bilgiler
        trends = []
        if trend_data:
            trends = trend_data.get('trends', [])
            print(f"📈 [PROMPT] Trends: {trends}")
        
        # Style'a göre base prompt
        style_prompts = {
            "modern": "modern digital art, clean design, professional layout,",
            "gaming": "gaming art, neon colors, futuristic design, digital illustration,",
            "minimal": "minimalist art, simple design, clean composition,",
            "trendy": "trendy digital art, vibrant colors, social media style,"
        }
        
        base_prompt = style_prompts.get(style, style_prompts["modern"])
        
        # Ana içerik
        main_content = visual_summary
        
        # Keywords'i prompt'a ekle
        if keywords:
            keywords_text = ", ".join(keywords[:5])
            main_content += f", featuring {keywords_text}"
        
        # Trends'i ekle
        if trends:
            trends_text = ", ".join(trends[:3])
            main_content += f", with {trends_text} elements"
        
        # Quality modifiers
        quality_suffix = ", high quality, detailed, professional, digital art, 4k, instagram ready"
        
        # Final prompt
        final_prompt = f"{base_prompt} {main_content}{quality_suffix}"
        
        print(f"✨ [PROMPT] Final prompt oluşturuldu ({len(final_prompt)} karakter)")
        print(f"📝 [PROMPT] Preview: {final_prompt[:100]}...")
        
        return final_prompt
    
    def _generate_with_stable_diffusion(self, prompt: str) -> Image.Image:
        """Stable Diffusion ile görsel üret - tam sizin örneğiniz gibi"""
        
        try:
            print(f"\n🤖 [DIFFUSION] Stable Diffusion generation başlıyor...")
            print(f"📝 [DIFFUSION] Prompt: {prompt}")
            print(f"🔧 [DIFFUSION] Device: {self.device}")
            
            # Generation parameters
            generation_params = {
                "prompt": prompt,
                "height": 512,
                "width": 512,
                "num_inference_steps": 20,
                "guidance_scale": 7.5,
                "negative_prompt": "blurry, low quality, distorted, ugly"
            }
            
            print(f"⚙️ [DIFFUSION] Parameters:")
            for key, value in generation_params.items():
                print(f"   • {key}: {value}")
            
            print(f"⏳ [DIFFUSION] Generating... (20 steps)")
            
            # Sizin örneğinizin aynısı
            import time
            start_time = time.time()
            
            result = self.pipe(**generation_params)
            image = result.images[0]  # İlk image'i al
            
            generation_time = time.time() - start_time
            
            print(f"✅ [DIFFUSION] Generation tamamlandı!")
            print(f"⏱️ [DIFFUSION] Süre: {generation_time:.2f} saniye")
            print(f"📏 [DIFFUSION] Image boyutu: {image.size}")
            
            return image
            
        except Exception as e:
            print(f"❌ [DIFFUSION] Generation hatası: {e}")
            raise
    
    def _resize_for_instagram(self, image: Image.Image) -> Image.Image:
        """AI image'i Instagram formatına çevir"""
        
        print(f"📱 [FORMAT] Instagram formatına çevriliyor...")
        
        # Instagram square format
        instagram_img = Image.new('RGB', self.poster_size, color='white')
        
        # AI image'i resize et ve merkeze yerleştir
        resized_image = image.resize((900, 900), Image.Resampling.LANCZOS)
        
        # Merkeze paste
        x = (self.poster_size[0] - 900) // 2
        y = (self.poster_size[1] - 900) // 2
        
        instagram_img.paste(resized_image, (x, y))
        
        print(f"✅ [FORMAT] Instagram formatı hazır: {instagram_img.size}")
        
        return instagram_img
    
    def _create_fallback_image(self, content_data: Dict[str, Any], style: str) -> str:
        """Fallback image oluştur"""
        
        print(f"🔄 [FALLBACK] Fallback image oluşturuluyor...")
        
        # Basit renkli image
        img = Image.new('RGB', self.poster_size, color='#3498DB')
        
        return self._save_image(img, f"{style}_fallback")
    
    def _save_image(self, img: Image.Image, prefix: str) -> str:
        """Image'i tmp'ye kaydet"""
        
        try:
            # tmp directory
            tmp_dir = os.path.join(os.path.dirname(__file__), "..", "tmp")
            os.makedirs(tmp_dir, exist_ok=True)
            
            # Unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            filename = f"{prefix}_{timestamp}_{unique_id}.png"
            filepath = os.path.join(tmp_dir, filename)
            
            # Save
            img.save(filepath, "PNG", quality=95)
            
            print(f"💾 [SAVE] Kaydedildi: {filename}")
            print(f"📁 [SAVE] Konum: {tmp_dir}")
            print(f"📏 [SAVE] Boyut: {img.size}")
            
            logger.info(f"Image saved: {filename}")
            
            return filepath
            
        except Exception as e:
            print(f"❌ [SAVE] Kayıt hatası: {e}")
            raise

# Singleton
_diffusion_generator = None

def get_diffusion_generator() -> DiffusionImageGenerator:
    global _diffusion_generator
    if _diffusion_generator is None:
        _diffusion_generator = DiffusionImageGenerator()
    return _diffusion_generator
