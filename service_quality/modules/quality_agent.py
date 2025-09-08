import os
import logging
from typing import Dict, Any, List, Optional, Tuple
import torch
import numpy as np
from PIL import Image
import cv2
from datetime import datetime

# Quality assessment imports - CLIP + LPIPS
try:
    from transformers import CLIPProcessor, CLIPModel, AutoModelForSequenceClassification, AutoProcessor
    from torchvision import transforms
    QUALITY_LIBS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Basic quality libraries not available: {e}")
    CLIPProcessor = None
    CLIPModel = None
    AutoModelForSequenceClassification = None
    AutoProcessor = None
    transforms = None
    QUALITY_LIBS_AVAILABLE = False

# LPIPS import (optional)
try:
    import lpips
    LPIPS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ LPIPS not available: {e}")
    lpips = None
    LPIPS_AVAILABLE = False

logger = logging.getLogger(__name__)

class QualityAgent:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.clip_model = None
        self.clip_processor = None
        self.aesthetic_model = None
        self.aesthetic_processor = None
        self.lpips_model = None
        self._setup_models()
        
    def _setup_models(self):
        """Quality assessment modellerini kurulum - CLIP ve Aesthetic Predictor"""
        
        print(f"🔧 [QUALITY] Setting up quality assessment models...")
        print(f"🔧 [QUALITY] Device: {self.device}")
        print(f"🔧 [QUALITY] Libraries available: {QUALITY_LIBS_AVAILABLE}")
        
        if not QUALITY_LIBS_AVAILABLE:
            print("⚠️ [QUALITY] Quality libraries not available")
            print("💡 [QUALITY] Install: pip install transformers torch")
            return
            
        try:
            # CLIP model for text-image similarity (sizin örneğinizin aynısı)
            print("📥 [QUALITY] Loading CLIP model...")
            self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            self.clip_model = self.clip_model.to(self.device)
            print("✅ [QUALITY] CLIP model loaded")
            
            # Aesthetic predictor model - alternatif model kullan
            print("📥 [QUALITY] Loading Aesthetic Predictor...")
            try:
                model_id = "shunk031/aesthetic-predictor"
                self.aesthetic_model = AutoModelForSequenceClassification.from_pretrained(model_id).to(self.device)
                self.aesthetic_processor = AutoProcessor.from_pretrained(model_id)
                print("✅ [QUALITY] Aesthetic Predictor loaded")
            except Exception as aesthetic_e:
                print(f"⚠️ [QUALITY] Aesthetic predictor failed, using CLIP fallback: {aesthetic_e}")
                self.aesthetic_model = None
                self.aesthetic_processor = None
            
            # LPIPS model for perceptual similarity (optional)
            if LPIPS_AVAILABLE:
                try:
                    print("📥 [QUALITY] Loading LPIPS model...")
                    self.lpips_model = lpips.LPIPS(net='alex').to(self.device)
                    print("✅ [QUALITY] LPIPS model loaded")
                except Exception as lpips_e:
                    print(f"⚠️ [QUALITY] LPIPS model failed: {lpips_e}")
                    self.lpips_model = None
            else:
                print("⚠️ [QUALITY] LPIPS not available - install with: pip install lpips")
            
            logger.info(f"Quality assessment models loaded on {self.device}")
            
        except Exception as e:
            print(f"❌ [QUALITY] Model setup failed: {e}")
            logger.error(f"Quality model setup failed: {e}")
            self.clip_model = None
            self.aesthetic_model = None
            self.lpips_model = None
    
    def assess_image_quality(self, image_path: str, 
                           prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Core quality assessment - CLIP + Aesthetic + Technical
        """
        try:
            print(f"\n🔍 [QUALITY] Starting quality assessment...")
            print(f"📁 [QUALITY] Image: {image_path}")
            print(f"📝 [QUALITY] Prompt: {prompt}")
            
            # Load image
            image = Image.open(image_path).convert('RGB')
            print(f"📏 [QUALITY] Image size: {image.size}")
            
            # CLIP Score - Text-Image Alignment
            clip_score = 0.5  # Default
            if self.clip_model and prompt:
                clip_score = self._calculate_clip_score(image, prompt)
            
            # Aesthetic Score
            aesthetic_score = 0.5  # Default
            if self.aesthetic_model:
                print(f"🎨 [AESTHETIC] Aesthetic model available, calculating real score...")
                aesthetic_score = self._calculate_aesthetic_score(image)
            else:
                print(f"🎨 [AESTHETIC] No aesthetic model, using CLIP-based estimation...")
                aesthetic_score = self._estimate_aesthetic_with_clip(image)
            
            # Technical quality metrics
            technical_metrics = self._calculate_technical_metrics(image)
            
            # Overall quality score
            overall_score = self._calculate_overall_score(
                clip_score, aesthetic_score, technical_metrics
            )
            
            result = {
                "image_path": image_path,
                "overall_score": overall_score,
                "clip_score": clip_score,
                "aesthetic_score": aesthetic_score,
                "technical_metrics": technical_metrics,
                "assessment_timestamp": datetime.now().isoformat(),
                "device_used": self.device
            }
            
            print(f"✅ [QUALITY] Assessment completed - Overall score: {overall_score.get('overall_score', 0)}")
            
            return result
            
        except Exception as e:
            print(f"❌ [QUALITY] Assessment failed: {e}")
            logger.error(f"Quality assessment failed: {e}")
            return {
                "error": str(e),
                "status": "failed",
                "image_path": image_path
            }
    
    def _calculate_clip_score(self, image: Image.Image, prompt: str) -> float:
        """CLIP Score - Fixed version"""
        
        print(f"🔗 [CLIP] Calculating CLIP score...")
        print(f"📝 [CLIP] Prompt: {prompt}")
        
        try:
            # CLIP similarity calculation - FIXED version
            print(f"🔧 [CLIP] Processing text and image...")
            
            # Separate text and image processing
            text_inputs = self.clip_processor.tokenizer([prompt], padding=True, return_tensors="pt")
            image_inputs = self.clip_processor.image_processor([image], return_tensors="pt")
            
            # Move to device
            text_inputs = {k: v.to(self.device) for k, v in text_inputs.items()}
            image_inputs = {k: v.to(self.device) for k, v in image_inputs.items()}
            
            with torch.no_grad():
                # Get separate embeddings
                text_features = self.clip_model.get_text_features(**text_inputs)
                image_features = self.clip_model.get_image_features(**image_inputs)
                
                print(f"🔍 [CLIP] Text features shape: {text_features.shape}")
                print(f"🔍 [CLIP] Image features shape: {image_features.shape}")
                
                # Normalize features
                text_features = text_features / text_features.norm(dim=-1, keepdim=True)
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)
                
                # Calculate cosine similarity
                similarity = torch.cosine_similarity(text_features, image_features, dim=-1).item()
                
                print(f"🔍 [CLIP] Raw cosine similarity: {similarity:.6f}")
                
                # Convert from [-1, 1] to [0, 1] for easier interpretation
                score = (similarity + 1) / 2
                
                print(f"🔍 [CLIP] Normalized score (0-1): {score:.6f}")
            
            print(f"✅ [CLIP] CLIP Similarity: {similarity:.4f}")
            print(f"✅ [CLIP] CLIP Score (normalized): {score:.4f}")
            
            return score
            
        except Exception as e:
            print(f"❌ [CLIP] CLIP score calculation failed: {e}")
            return 0.5  # Default score
    
    def _calculate_aesthetic_score(self, image: Image.Image) -> float:
        """Aesthetic Score - CLIP-based fallback"""
        
        print(f"🎨 [AESTHETIC] Calculating aesthetic score...")
        
        if not self.aesthetic_model:
            print(f"⚠️ [AESTHETIC] No aesthetic model, using CLIP-based estimation")
            return self._estimate_aesthetic_with_clip(image)
        
        try:
            # Sizin verdiğiniz örneğin aynısı (eğer model varsa)
            inputs = self.aesthetic_processor(images=image, return_tensors="pt")
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                score = self.aesthetic_model(**inputs).logits.item()
            
            # Normalize score to 0-1 range
            normalized_score = (score + 10) / 20
            normalized_score = max(0.0, min(1.0, normalized_score))
            
            print(f"✅ [AESTHETIC] Aesthetic Score: {score} (normalized: {normalized_score})")
            
            return normalized_score
            
        except Exception as e:
            print(f"❌ [AESTHETIC] Aesthetic score calculation failed: {e}")
            return self._estimate_aesthetic_with_clip(image)
    
    def _estimate_aesthetic_with_clip(self, image: Image.Image) -> float:
        """CLIP ile aesthetic estimation"""
        
        try:
            # Aesthetic prompts
            aesthetic_prompts = [
                "beautiful, high quality, aesthetic, pleasing",
                "ugly, low quality, bad, unpleasant"
            ]
            
            if not self.clip_model:
                return 0.5
            
            inputs = self.clip_processor(
                text=aesthetic_prompts,
                images=[image], 
                return_tensors="pt", 
                padding=True
            )
            
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.clip_model(**inputs)
                probs = outputs.logits_per_image.softmax(dim=1)
                aesthetic_prob = probs[0][0].item()  # Beautiful vs ugly
            
            print(f"✅ [AESTHETIC] CLIP-based aesthetic: {aesthetic_prob}")
            return aesthetic_prob
            
        except Exception as e:
            print(f"❌ [AESTHETIC] CLIP aesthetic estimation failed: {e}")
            return 0.5
    
    def _calculate_technical_metrics(self, image: Image.Image) -> Dict[str, Any]:
        """Technical quality metrics - simplified"""
        
        print(f"🔧 [TECHNICAL] Calculating technical metrics...")
        
        try:
            img_array = np.array(image)
            
            # Sharpness (Laplacian variance)
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Noise level estimation
            noise_level = self._estimate_noise_level(gray)
            
            # Exposure quality
            exposure_quality = self._calculate_exposure_quality(img_array)
            
            metrics = {
                "sharpness": round(float(sharpness), 2),
                "noise_level": round(float(noise_level), 4),
                "exposure_quality": round(float(exposure_quality), 3)
            }
            
            print(f"✅ [TECHNICAL] Technical metrics calculated")
            return metrics
            
        except Exception as e:
            print(f"❌ [TECHNICAL] Technical calculation failed: {e}")
            return {"sharpness": 0, "noise_level": 1, "exposure_quality": 0}
    
    def _estimate_noise_level(self, gray_image: np.ndarray) -> float:
        """Estimate noise level in image"""
        
        # Use Laplacian to estimate noise
        laplacian = cv2.Laplacian(gray_image, cv2.CV_64F)
        noise_estimate = np.var(laplacian)
        
        # Normalize (empirical normalization)
        noise_level = min(1.0, noise_estimate / 10000)
        
        return noise_level
    
    def _calculate_exposure_quality(self, img_array: np.ndarray) -> float:
        """Exposure quality based on histogram distribution"""
        
        # Convert to grayscale for luminance analysis
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Histogram
        hist, _ = np.histogram(gray, bins=256, range=(0, 256))
        hist_norm = hist / np.sum(hist)
        
        # Check for clipping (overexposure/underexposure)
        underexposed = hist_norm[0:10].sum()  # Very dark pixels
        overexposed = hist_norm[245:256].sum()  # Very bright pixels
        
        # Well-exposed regions (middle range)
        well_exposed = hist_norm[50:200].sum()
        
        # Exposure quality score
        exposure_quality = well_exposed * (1 - underexposed - overexposed)
        
        return exposure_quality
    
    def _calculate_overall_score(self, clip_score: float, aesthetic_score: float,
                               technical_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Overall quality score - CLIP + Aesthetic + Technical kombinasyonu"""
        
        print(f"🎯 [OVERALL] Calculating overall quality score...")
        print(f"🔗 [OVERALL] CLIP Score: {clip_score}")
        print(f"🎨 [OVERALL] Aesthetic Score: {aesthetic_score}")
        
        # Weights
        weights = {
            "clip_alignment": 0.4,      # Text-image uyumu en önemli
            "aesthetic_quality": 0.35,   # Estetik kalite
            "technical_quality": 0.25    # Teknik kalite
        }
        
        # Technical score calculation
        technical_score = 0
        sharpness = technical_metrics.get("sharpness", 0)
        noise_level = technical_metrics.get("noise_level", 1)
        exposure = technical_metrics.get("exposure_quality", 0)
        
        # Technical scoring
        if sharpness > 100:  # Good sharpness
            technical_score += 0.4
        elif sharpness > 50:
            technical_score += 0.2
        
        if noise_level < 0.1:  # Low noise
            technical_score += 0.3
        elif noise_level < 0.2:
            technical_score += 0.15
        
        if exposure > 0.6:  # Good exposure
            technical_score += 0.3
        elif exposure > 0.4:
            technical_score += 0.15
        
        # Weighted overall score
        overall = (
            clip_score * weights["clip_alignment"] +
            aesthetic_score * weights["aesthetic_quality"] +
            technical_score * weights["technical_quality"]
        )
        
        # Quality level interpretation
        if overall >= 0.8:
            quality_level = "excellent"
            quality_description = "Mükemmel kalite - Text-image uyumu ve estetik değerler yüksek"
        elif overall >= 0.65:
            quality_level = "good"
            quality_description = "İyi kalite - Çoğu metrikte başarılı performans"
        elif overall >= 0.45:
            quality_level = "fair"
            quality_description = "Orta kalite - Bazı iyileştirmeler gerekli"
        else:
            quality_level = "poor"
            quality_description = "Düşük kalite - Önemli iyileştirmeler gerekli"
        
        return {
            "overall_score": round(overall, 3),
            "quality_level": quality_level,
            "quality_description": quality_description,
            "component_scores": {
                "clip_alignment": round(clip_score, 3),
                "aesthetic_quality": round(aesthetic_score, 3),
                "technical_quality": round(technical_score, 3)
            },
            "raw_scores": {
                "clip_score": round(clip_score, 4),
                "aesthetic_score": round(aesthetic_score, 4),
                "technical_sharpness": round(sharpness, 2),
                "technical_noise": round(noise_level, 4),
                "technical_exposure": round(exposure, 3)
            },
            "weights_used": weights,
            "scoring_method": "clip_aesthetic_technical"
        }

# Singleton instance
_quality_agent = None

def get_quality_agent() -> QualityAgent:
    global _quality_agent
    if _quality_agent is None:
        _quality_agent = QualityAgent()
    return _quality_agent