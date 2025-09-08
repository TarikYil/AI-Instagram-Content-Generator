import logging
from typing import Dict, Any, List, Optional
import random
from datetime import datetime

logger = logging.getLogger(__name__)

class QualityBasedFinalizationAgent:
    def __init__(self):
        self.hashtag_database = self._load_hashtag_database()
        self.quality_thresholds = {
            "excellent": 0.8,
            "good": 0.65,
            "fair": 0.45,
            "poor": 0.0
        }
        
    def _load_hashtag_database(self) -> Dict[str, List[str]]:
        """Quality-based hashtag database"""
        
        return {
            # Quality level based hashtags
            "excellent_quality": [
                "#perfectshot", "#highquality", "#professional", "#stunning", 
                "#masterpiece", "#premium", "#flawless", "#crisp"
            ],
            "good_quality": [
                "#goodquality", "#nice", "#solid", "#decent", "#clean", 
                "#sharp", "#clear", "#wellmade"
            ],
            "fair_quality": [
                "#okay", "#average", "#standard", "#basic", "#simple",
                "#everyday", "#casual", "#normal"
            ],
            
            # CLIP alignment based hashtags
            "perfect_alignment": [
                "#accurate", "#onpoint", "#perfect", "#exactmatch", 
                "#nailed", "#spoton", "#precise"
            ],
            "good_alignment": [
                "#close", "#goodmatch", "#aligned", "#fitting", "#suitable"
            ],
            "poor_alignment": [
                "#abstract", "#artistic", "#creative", "#interpretation", "#unique"
            ],
            
            # Aesthetic quality hashtags
            "high_aesthetic": [
                "#beautiful", "#gorgeous", "#aesthetic", "#pleasing", 
                "#attractive", "#elegant", "#stylish", "#artistic"
            ],
            "medium_aesthetic": [
                "#nice", "#decent", "#okay", "#average", "#standard"
            ],
            
            # Technical quality hashtags
            "sharp_image": [
                "#sharp", "#crisp", "#clear", "#detailed", "#hd", "#highres"
            ],
            "soft_image": [
                "#soft", "#dreamy", "#gentle", "#smooth", "#artistic"
            ],
            
            # Style-specific hashtags
            "gaming": [
                "#gaming", "#gamer", "#videogames", "#mobilegaming", "#gamedev",
                "#esports", "#gameplay", "#gameart", "#indiegame", "#retrogaming"
            ],
            "modern": [
                "#modern", "#contemporary", "#sleek", "#minimal", "#clean",
                "#professional", "#business", "#tech", "#digital", "#ui"
            ],
            "trendy": [
                "#trendy", "#viral", "#trending", "#popular", "#hot",
                "#latest", "#new", "#fresh", "#cool", "#awesome"
            ],
            "minimal": [
                "#minimal", "#minimalist", "#simple", "#clean", "#pure",
                "#elegant", "#sophisticated", "#refined", "#subtle"
            ],
            
            # Content type hashtags
            "ai_generated": [
                "#ai", "#aiart", "#artificialintelligence", "#machinelearning",
                "#generated", "#synthetic", "#digital", "#computational"
            ],
            "instagram_ready": [
                "#instagram", "#insta", "#ig", "#post", "#content", "#social",
                "#socialmedia", "#feed", "#story", "#reel"
            ]
        }
    
    def finalize_content_with_quality(self, 
                                    image_path: str,
                                    quality_assessment: Dict[str, Any],
                                    original_prompt: str,
                                    style: str = "modern",
                                    platform: str = "instagram") -> Dict[str, Any]:
        """
        Quality assessment'a göre content finalization
        """
        
        print(f"🎯 [FINALIZE] Starting quality-based finalization...")
        print(f"📁 [FINALIZE] Image: {image_path}")
        print(f"🎨 [FINALIZE] Style: {style}")
        print(f"📱 [FINALIZE] Platform: {platform}")
        
        try:
            # Quality scores çıkar
            overall_score = quality_assessment.get("overall_score", {})
            quality_level = overall_score.get("quality_level", "fair")
            clip_score = overall_score.get("raw_scores", {}).get("clip_score", 0.5)
            aesthetic_score = overall_score.get("raw_scores", {}).get("aesthetic_score", 0.5)
            technical_metrics = quality_assessment.get("technical_metrics", {})
            
            print(f"📊 [FINALIZE] Quality level: {quality_level}")
            print(f"🔗 [FINALIZE] CLIP score: {clip_score}")
            print(f"🎨 [FINALIZE] Aesthetic score: {aesthetic_score}")
            
            # Quality-based hashtag generation
            hashtags = self._generate_quality_hashtags(
                quality_level, clip_score, aesthetic_score, technical_metrics, style
            )
            
            # Quality-based caption enhancement
            caption = self._generate_quality_caption(
                original_prompt, quality_assessment, style, platform
            )
            
            # Platform optimization
            optimized_content = self._optimize_for_platform(
                caption, hashtags, quality_assessment, platform
            )
            
            # Quality recommendations
            recommendations = self._generate_quality_recommendations(quality_assessment)
            
            result = {
                "finalized_content": {
                    "caption": optimized_content["caption"],
                    "hashtags": optimized_content["hashtags"],
                    "quality_tags": hashtags["quality_specific"],
                    "platform_optimized": True
                },
                "quality_insights": {
                    "overall_score": overall_score.get("overall_score", 0),
                    "quality_level": quality_level,
                    "clip_alignment": clip_score,
                    "aesthetic_quality": aesthetic_score,
                    "recommendations": recommendations
                },
                "metadata": {
                    "original_prompt": original_prompt,
                    "style": style,
                    "platform": platform,
                    "finalization_timestamp": datetime.now().isoformat(),
                    "quality_based": True
                }
            }
            
            print(f"✅ [FINALIZE] Content finalization completed")
            return result
            
        except Exception as e:
            print(f"❌ [FINALIZE] Finalization failed: {e}")
            logger.error(f"Content finalization failed: {e}")
            return {
                "error": str(e),
                "status": "failed"
            }
    
    def _generate_quality_hashtags(self, quality_level: str, clip_score: float, 
                                 aesthetic_score: float, technical_metrics: Dict[str, Any],
                                 style: str) -> Dict[str, List[str]]:
        """Quality assessment'a göre hashtag generation"""
        
        print(f"🏷️ [HASHTAGS] Generating quality-based hashtags...")
        
        hashtags = {
            "quality_specific": [],
            "alignment_based": [],
            "aesthetic_based": [],
            "technical_based": [],
            "style_based": [],
            "platform_based": []
        }
        
        # Quality level hashtags
        if quality_level == "excellent":
            hashtags["quality_specific"].extend(
                random.sample(self.hashtag_database["excellent_quality"], 2)
            )
        elif quality_level == "good":
            hashtags["quality_specific"].extend(
                random.sample(self.hashtag_database["good_quality"], 2)
            )
        elif quality_level == "fair":
            hashtags["quality_specific"].extend(
                random.sample(self.hashtag_database["fair_quality"], 1)
            )
        
        # CLIP alignment hashtags
        if clip_score >= 0.8:
            hashtags["alignment_based"].extend(
                random.sample(self.hashtag_database["perfect_alignment"], 1)
            )
        elif clip_score >= 0.6:
            hashtags["alignment_based"].extend(
                random.sample(self.hashtag_database["good_alignment"], 1)
            )
        else:
            hashtags["alignment_based"].extend(
                random.sample(self.hashtag_database["poor_alignment"], 1)
            )
        
        # Aesthetic hashtags
        if aesthetic_score >= 0.7:
            hashtags["aesthetic_based"].extend(
                random.sample(self.hashtag_database["high_aesthetic"], 2)
            )
        else:
            hashtags["aesthetic_based"].extend(
                random.sample(self.hashtag_database["medium_aesthetic"], 1)
            )
        
        # Technical quality hashtags
        sharpness = technical_metrics.get("sharpness", 0)
        if sharpness > 100:
            hashtags["technical_based"].extend(
                random.sample(self.hashtag_database["sharp_image"], 1)
            )
        else:
            hashtags["technical_based"].extend(
                random.sample(self.hashtag_database["soft_image"], 1)
            )
        
        # Style hashtags
        if style in self.hashtag_database:
            hashtags["style_based"].extend(
                random.sample(self.hashtag_database[style], 3)
            )
        
        # AI generated hashtags
        hashtags["platform_based"].extend(
            random.sample(self.hashtag_database["ai_generated"], 2)
        )
        hashtags["platform_based"].extend(
            random.sample(self.hashtag_database["instagram_ready"], 2)
        )
        
        print(f"✅ [HASHTAGS] Generated {sum(len(v) for v in hashtags.values())} hashtags")
        return hashtags
    
    def _generate_quality_caption(self, original_prompt: str, 
                                quality_assessment: Dict[str, Any],
                                style: str, platform: str) -> str:
        """Quality assessment'a göre caption generation"""
        
        print(f"📝 [CAPTION] Generating quality-based caption...")
        
        overall_score = quality_assessment.get("overall_score", {})
        quality_level = overall_score.get("quality_level", "fair")
        clip_score = overall_score.get("raw_scores", {}).get("clip_score", 0.5)
        aesthetic_score = overall_score.get("raw_scores", {}).get("aesthetic_score", 0.5)
        
        # Quality-based intro
        quality_intros = {
            "excellent": ["🎯 Perfect shot!", "✨ Masterpiece alert!", "🔥 Incredible quality!"],
            "good": ["👍 Great result!", "✅ Nice work!", "🎨 Good quality!"],
            "fair": ["📸 Decent shot", "🎯 Not bad", "📱 Standard quality"],
            "poor": ["🎨 Artistic attempt", "📸 Creative shot", "🎯 Experimental"]
        }
        
        intro = random.choice(quality_intros.get(quality_level, quality_intros["fair"]))
        
        # CLIP alignment comment
        alignment_comments = {
            "high": "Perfect match with the concept!",
            "medium": "Good representation of the idea.",
            "low": "Creative interpretation of the theme."
        }
        
        if clip_score >= 0.8:
            alignment_comment = alignment_comments["high"]
        elif clip_score >= 0.6:
            alignment_comment = alignment_comments["medium"]
        else:
            alignment_comment = alignment_comments["low"]
        
        # Aesthetic comment
        aesthetic_comments = {
            "high": "Visually stunning and pleasing!",
            "medium": "Nice visual appeal.",
            "low": "Unique artistic style."
        }
        
        if aesthetic_score >= 0.7:
            aesthetic_comment = aesthetic_comments["high"]
        elif aesthetic_score >= 0.5:
            aesthetic_comment = aesthetic_comments["medium"]
        else:
            aesthetic_comment = aesthetic_comments["low"]
        
        # Style-based ending
        style_endings = {
            "gaming": "Ready to level up! 🎮",
            "modern": "Professional and sleek. 💼",
            "minimal": "Less is more. ✨",
            "trendy": "Totally trending! 🔥"
        }
        
        ending = style_endings.get(style, "Amazing creation! 🎨")
        
        # Combine caption
        caption = f"{intro} {alignment_comment} {aesthetic_comment} {ending}"
        
        print(f"✅ [CAPTION] Quality-based caption generated")
        return caption
    
    def _optimize_for_platform(self, caption: str, hashtags: Dict[str, List[str]], 
                              quality_assessment: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """Platform optimization"""
        
        print(f"📱 [PLATFORM] Optimizing for {platform}...")
        
        # Flatten hashtags
        all_hashtags = []
        for category, tags in hashtags.items():
            all_hashtags.extend(tags)
        
        # Platform-specific optimization
        if platform == "instagram":
            # Instagram: Max 30 hashtags, optimal 10-15
            selected_hashtags = all_hashtags[:12]
            
            # Add quality indicator emoji
            overall_score = quality_assessment.get("overall_score", {}).get("overall_score", 0)
            if overall_score >= 0.8:
                caption = f"✨ {caption}"
            elif overall_score >= 0.65:
                caption = f"👍 {caption}"
            else:
                caption = f"🎨 {caption}"
                
        elif platform == "twitter":
            # Twitter: Character limit, fewer hashtags
            selected_hashtags = all_hashtags[:5]
            caption = caption[:200]  # Shorter for Twitter
            
        else:
            # Default platform
            selected_hashtags = all_hashtags[:10]
        
        return {
            "caption": caption,
            "hashtags": selected_hashtags,
            "total_hashtags": len(selected_hashtags)
        }
    
    def _generate_quality_recommendations(self, quality_assessment: Dict[str, Any]) -> List[str]:
        """Quality-based improvement recommendations"""
        
        recommendations = []
        
        overall_score = quality_assessment.get("overall_score", {})
        raw_scores = overall_score.get("raw_scores", {})
        
        # CLIP score recommendations
        clip_score = raw_scores.get("clip_score", 0.5)
        if clip_score < 0.6:
            recommendations.append("Improve prompt specificity for better text-image alignment")
        
        # Aesthetic recommendations
        aesthetic_score = raw_scores.get("aesthetic_score", 0.5)
        if aesthetic_score < 0.6:
            recommendations.append("Consider enhancing visual appeal with better composition")
        
        # Technical recommendations
        sharpness = raw_scores.get("technical_sharpness", 0)
        if sharpness < 100:
            recommendations.append("Increase image sharpness with higher resolution generation")
        
        noise_level = raw_scores.get("technical_noise", 0)
        if noise_level > 0.1:
            recommendations.append("Reduce noise by adjusting generation parameters")
        
        # Style-specific recommendations
        quality_level = overall_score.get("quality_level", "fair")
        if quality_level == "poor":
            recommendations.append("Consider regenerating with different parameters")
        elif quality_level == "fair":
            recommendations.append("Fine-tune generation settings for better quality")
        
        return recommendations[:5]  # Max 5 recommendations
    
    def generate_quality_hashtags_only(self, quality_assessment: Dict[str, Any], 
                                     style: str = "modern", 
                                     max_hashtags: int = 15) -> List[str]:
        """Sadece hashtag generation - quality assessment'a göre"""
        
        print(f"🏷️ [HASHTAGS ONLY] Generating quality-based hashtags...")
        
        overall_score = quality_assessment.get("overall_score", {})
        quality_level = overall_score.get("quality_level", "fair")
        raw_scores = overall_score.get("raw_scores", {})
        
        hashtags = []
        
        # Quality level hashtags
        quality_key = f"{quality_level}_quality"
        if quality_key in self.hashtag_database:
            hashtags.extend(random.sample(self.hashtag_database[quality_key], 2))
        
        # Style hashtags
        if style in self.hashtag_database:
            hashtags.extend(random.sample(self.hashtag_database[style], 3))
        
        # CLIP alignment hashtags
        clip_score = raw_scores.get("clip_score", 0.5)
        if clip_score >= 0.8:
            hashtags.extend(random.sample(self.hashtag_database["perfect_alignment"], 1))
        elif clip_score >= 0.6:
            hashtags.extend(random.sample(self.hashtag_database["good_alignment"], 1))
        
        # Aesthetic hashtags
        aesthetic_score = raw_scores.get("aesthetic_score", 0.5)
        if aesthetic_score >= 0.7:
            hashtags.extend(random.sample(self.hashtag_database["high_aesthetic"], 2))
        else:
            hashtags.extend(random.sample(self.hashtag_database["medium_aesthetic"], 1))
        
        # Technical hashtags
        sharpness = raw_scores.get("technical_sharpness", 0)
        if sharpness > 100:
            hashtags.extend(random.sample(self.hashtag_database["sharp_image"], 1))
        
        # AI and platform hashtags
        hashtags.extend(random.sample(self.hashtag_database["ai_generated"], 2))
        hashtags.extend(random.sample(self.hashtag_database["instagram_ready"], 2))
        
        # Remove duplicates and limit
        unique_hashtags = list(dict.fromkeys(hashtags))[:max_hashtags]
        
        print(f"✅ [HASHTAGS ONLY] Generated {len(unique_hashtags)} quality-based hashtags")
        return unique_hashtags
    
    def get_quality_insights(self, quality_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Quality assessment'dan insight'lar çıkar"""
        
        overall_score = quality_assessment.get("overall_score", {})
        raw_scores = overall_score.get("raw_scores", {})
        
        insights = {
            "quality_summary": {
                "level": overall_score.get("quality_level", "unknown"),
                "score": overall_score.get("overall_score", 0),
                "description": overall_score.get("quality_description", "")
            },
            "strengths": [],
            "weaknesses": [],
            "hashtag_strategy": ""
        }
        
        # Strengths identification
        clip_score = raw_scores.get("clip_score", 0.5)
        aesthetic_score = raw_scores.get("aesthetic_score", 0.5)
        sharpness = raw_scores.get("technical_sharpness", 0)
        
        if clip_score >= 0.8:
            insights["strengths"].append("Excellent text-image alignment")
        if aesthetic_score >= 0.7:
            insights["strengths"].append("High aesthetic appeal")
        if sharpness > 150:
            insights["strengths"].append("Very sharp and detailed")
        
        # Weaknesses identification
        if clip_score < 0.5:
            insights["weaknesses"].append("Poor prompt matching")
        if aesthetic_score < 0.5:
            insights["weaknesses"].append("Low aesthetic quality")
        if sharpness < 50:
            insights["weaknesses"].append("Image appears blurry")
        
        # Hashtag strategy
        quality_level = overall_score.get("quality_level", "fair")
        if quality_level == "excellent":
            insights["hashtag_strategy"] = "Use premium quality hashtags to highlight excellence"
        elif quality_level == "good":
            insights["hashtag_strategy"] = "Focus on positive quality indicators"
        else:
            insights["hashtag_strategy"] = "Emphasize artistic and creative aspects"
        
        return insights

# Singleton instance
_finalization_agent = None

def get_finalization_agent() -> QualityBasedFinalizationAgent:
    global _finalization_agent
    if _finalization_agent is None:
        _finalization_agent = QualityBasedFinalizationAgent()
    return _finalization_agent
