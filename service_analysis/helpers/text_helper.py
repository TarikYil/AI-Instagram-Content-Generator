from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import re
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

# NLTK verilerini indir (ilk çalıştırmada)
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)

class TextProcessor:
    def __init__(self):
        self.sentence_model = None
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))
        
    def _load_sentence_model(self):
        """Sentence transformer modelini lazy loading ile yükle"""
        if self.sentence_model is None:
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("✅ Sentence Transformer modeli yüklendi")
        return self.sentence_model
    
    def clean_text(self, text: str) -> str:
        """Metni temizle ve normalize et"""
        if not text:
            return ""
        
        # Küçük harfe çevir
        text = text.lower()
        
        # Özel karakterleri temizle
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        
        # Fazla boşlukları temizle
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """TF-IDF kullanarak anahtar kelimeleri çıkar"""
        try:
            if not text:
                return []
            
            # Metni temizle
            clean_text = self.clean_text(text)
            
            # Tokenize et
            tokens = word_tokenize(clean_text)
            
            # Stop words'leri filtrele ve stem et
            filtered_tokens = []
            for token in tokens:
                if token not in self.stop_words and len(token) > 2:
                    stemmed = self.stemmer.stem(token)
                    filtered_tokens.append(stemmed)
            
            if not filtered_tokens:
                return []
            
            # TF-IDF ile anahtar kelimeleri bul
            vectorizer = TfidfVectorizer(max_features=max_keywords * 2)
            tfidf_matrix = vectorizer.fit_transform([' '.join(filtered_tokens)])
            
            # Feature names ve scores'ları al
            feature_names = vectorizer.get_feature_names_out()
            tfidf_scores = tfidf_matrix.toarray()[0]
            
            # Score'lara göre sırala
            word_scores = list(zip(feature_names, tfidf_scores))
            word_scores.sort(key=lambda x: x[1], reverse=True)
            
            # En yüksek score'lu kelimeleri döndür
            keywords = [word for word, score in word_scores[:max_keywords] if score > 0]
            
            return keywords
            
        except Exception as e:
            logger.error(f"Keyword extraction hatası: {e}")
            return []
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Metinler için embeddings oluştur"""
        try:
            model = self._load_sentence_model()
            embeddings = model.encode(texts)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Embedding generation hatası: {e}")
            return []
    
    def find_similar_texts(self, query_text: str, candidate_texts: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        """Query text'e benzer metinleri bul"""
        try:
            model = self._load_sentence_model()
            
            # Embeddings oluştur
            query_embedding = model.encode([query_text])
            candidate_embeddings = model.encode(candidate_texts)
            
            # Cosine similarity hesapla
            similarities = cosine_similarity(query_embedding, candidate_embeddings)[0]
            
            # Sonuçları sırala
            results = []
            for i, similarity in enumerate(similarities):
                results.append({
                    "text": candidate_texts[i],
                    "similarity": float(similarity),
                    "index": i
                })
            
            # Similarity'ye göre sırala ve top_k döndür
            results.sort(key=lambda x: x["similarity"], reverse=True)
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Text similarity hatası: {e}")
            return []
    
    def analyze_aso_keywords(self, title: str, description: str, current_keywords: List[str] = None) -> Dict[str, Any]:
        """ASO için keyword analizi yap"""
        try:
            all_text = f"{title} {description}".strip()
            
            # Mevcut text'ten keyword'leri çıkar
            extracted_keywords = self.extract_keywords(all_text, max_keywords=15)
            
            # Mevcut keyword'lerle birleştir
            if current_keywords:
                combined_keywords = list(set(extracted_keywords + current_keywords))
            else:
                combined_keywords = extracted_keywords
            
            # Keyword'leri analiz et
            keyword_analysis = []
            for keyword in combined_keywords[:10]:  # En iyi 10 keyword
                # Keyword'ün text içindeki frequency'sini hesapla
                frequency = all_text.lower().count(keyword.lower())
                
                keyword_analysis.append({
                    "keyword": keyword,
                    "frequency": frequency,
                    "relevance_score": frequency / len(all_text.split()) if all_text else 0
                })
            
            # Relevance score'a göre sırala
            keyword_analysis.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            return {
                "extracted_keywords": extracted_keywords,
                "recommended_keywords": [kw["keyword"] for kw in keyword_analysis[:5]],
                "keyword_analysis": keyword_analysis,
                "total_keywords": len(combined_keywords)
            }
            
        except Exception as e:
            logger.error(f"ASO keyword analizi hatası: {e}")
            return {
                "extracted_keywords": [],
                "recommended_keywords": [],
                "keyword_analysis": [],
                "total_keywords": 0
            }
    
    def summarize_content(self, visual_captions: List[str], video_captions: List[str] = None) -> Dict[str, str]:
        """Görsel ve video caption'larından özet oluştur"""
        try:
            # Visual summary
            visual_summary = ""
            if visual_captions:
                # En uzun ve anlamlı caption'ı seç
                visual_captions_clean = [cap for cap in visual_captions if cap and len(cap.strip()) > 10]
                if visual_captions_clean:
                    visual_summary = max(visual_captions_clean, key=len)
                else:
                    visual_summary = "Visual content detected"
            
            # Video summary
            video_summary = ""
            if video_captions:
                video_captions_clean = [cap for cap in video_captions if cap and len(cap.strip()) > 10]
                if video_captions_clean:
                    # Video için birden fazla caption'ı birleştir
                    unique_captions = list(set(video_captions_clean))
                    if len(unique_captions) > 1:
                        video_summary = f"Video shows: {', '.join(unique_captions[:3])}"
                    else:
                        video_summary = unique_captions[0]
                else:
                    video_summary = "Video content detected"
            
            return {
                "visual_summary": visual_summary,
                "video_summary": video_summary
            }
            
        except Exception as e:
            logger.error(f"Content summarization hatası: {e}")
            return {
                "visual_summary": "Content analysis failed",
                "video_summary": "Content analysis failed"
            }


# Singleton instance
_text_processor = None

def get_text_processor() -> TextProcessor:
    global _text_processor
    if _text_processor is None:
        _text_processor = TextProcessor()
    return _text_processor
