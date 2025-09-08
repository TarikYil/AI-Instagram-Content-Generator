"""
AI Content Pipeline Workflow Manager
"""
import streamlit as st
from typing import Dict, Any, List, Optional
import time
from services.microservice_client import get_microservice_client

class WorkflowManager:
    def __init__(self):
        self.client = get_microservice_client()
    
    def reset_workflow_state(self):
        """Workflow durumunu sıfırla"""
        st.session_state.workflow_state = {
            'step': 0,  # 0: Upload, 1: Process, 2: Generate, 3: Quality
            'trend_data': None,
            'analysis_data': None,
            'generation_data': None,
            'quality_data': None,
            'uploaded_files': [],
            'status_logs': [],
            'final_output': None
        }
    
    def add_status_log(self, message: str, status: str = "info"):
        """Status log ekle"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = {
            'time': timestamp,
            'message': message,
            'status': status  # info, success, error, warning
        }
        st.session_state.workflow_state['status_logs'].append(log_entry)
    
    def get_status_logs(self) -> List[Dict]:
        """Status logları al"""
        return st.session_state.workflow_state.get('status_logs', [])
    
    def check_services_health(self) -> Dict[str, bool]:
        """Tüm servislerin sağlığını kontrol et"""
        return self.client.check_all_services()
    
    def upload_materials(self, uploaded_files: List, keywords: List[str], description: str) -> bool:
        """Materyalleri yükle"""
        try:
            self.add_status_log("📤 Materyaller yükleniyor...", "info")
            
            # Dosyaları upload servisine gönder
            file_bytes_list = []
            for uploaded_file in uploaded_files:
                # Dosyayı baştan oku (seek to beginning)
                uploaded_file.seek(0)
                file_bytes_list.append(uploaded_file.read())
            
            upload_result = self.client.upload_images(file_bytes_list)
            
            if upload_result.get('success', False):
                st.session_state.workflow_state['uploaded_files'] = upload_result.get('assets', {}).get('images', [])
                st.session_state.workflow_state['keywords'] = keywords
                st.session_state.workflow_state['description'] = description
                st.session_state.workflow_state['step'] = 1  # Upload tamamlandı, process için hazır
                
                uploaded_count = upload_result.get('uploaded_count', len(uploaded_files))
                self.add_status_log(f"✅ {uploaded_count} dosya başarıyla yüklendi", "success")
                self.add_status_log("🎯 Process adımı için hazır", "info")
                return True
            else:
                error_msg = upload_result.get('error', 'Bilinmeyen hata')
                self.add_status_log(f"❌ Yükleme hatası: {error_msg}", "error")
                return False
                
        except Exception as e:
            self.add_status_log(f"❌ Yükleme sırasında hata: {str(e)}", "error")
            return False
    
    def start_process(self) -> bool:
        """Trend analizi ve materyal analizini başlat"""
        try:
            self.add_status_log("🚀 İşlem başlatılıyor...", "info")
            
            # 1. Trend analizi
            self.add_status_log("📈 YouTube trend analizi yapılıyor...", "info")
            trend_result = self.client.get_youtube_trends()
            
            if trend_result.get('error'):
                self.add_status_log(f"⚠️ Trend analizi hatası: {trend_result['error']}", "warning")
                st.session_state.workflow_state['trend_data'] = {"trends": [], "hashtags": []}
            else:
                st.session_state.workflow_state['trend_data'] = trend_result
                trend_count = len(trend_result.get('trends', []))
                self.add_status_log(f"✅ {trend_count} trend analizi tamamlandı", "success")
            
            # 2. Materyal analizi
            self.add_status_log("🔍 Yüklenen materyaller analiz ediliyor...", "info")
            keywords = st.session_state.workflow_state.get('keywords', [])
            description = st.session_state.workflow_state.get('description', '')
            
            analysis_result = self.client.analyze_drive_content(keywords=keywords)
            
            if analysis_result.get('error'):
                self.add_status_log(f"❌ Materyal analizi hatası: {analysis_result['error']}", "error")
                return False
            else:
                st.session_state.workflow_state['analysis_data'] = analysis_result
                keyword_count = len(analysis_result.get('keywords', []))
                self.add_status_log(f"✅ Materyal analizi tamamlandı - {keyword_count} anahtar kelime", "success")
            
            # Workflow step'i güncelle
            st.session_state.workflow_state['step'] = 2
            self.add_status_log("🎯 İşlem tamamlandı - Görsel üretimi için hazır", "success")
            return True
            
        except Exception as e:
            self.add_status_log(f"❌ İşlem sırasında hata: {str(e)}", "error")
            return False
    
    def generate_content(self, style: str = "modern") -> bool:
        """İçerik ve görsel üret"""
        try:
            self.add_status_log("🎨 İçerik üretimi başlatılıyor...", "info")
            
            # Analiz verilerini al
            analysis_data = st.session_state.workflow_state.get('analysis_data', {})
            trend_data = st.session_state.workflow_state.get('trend_data', {})
            
            visual_summary = analysis_data.get('visual_summary', 'AI generated content')
            video_summary = analysis_data.get('video_summary', '')
            keywords = analysis_data.get('keywords', [])
            trends = trend_data.get('trends', [])[:5]  # İlk 5 trend
            
            self.add_status_log(f"📝 Prompt hazırlanıyor - {len(keywords)} anahtar kelime, {len(trends)} trend", "info")
            
            # Generation servisini çağır
            generation_result = self.client.generate_instagram_content(
                visual_summary=visual_summary,
                video_summary=video_summary,
                keywords=keywords,
                trends=trends,
                style=style
            )
            
            if generation_result.get('error'):
                self.add_status_log(f"❌ İçerik üretimi hatası: {generation_result['error']}", "error")
                return False
            else:
                st.session_state.workflow_state['generation_data'] = generation_result
                filename = generation_result.get('filename', 'Bilinmiyor')
                self.add_status_log(f"✅ Görsel üretildi: {filename}", "success")
                
                # Workflow step'i güncelle
                st.session_state.workflow_state['step'] = 3
                return True
                
        except Exception as e:
            self.add_status_log(f"❌ İçerik üretimi sırasında hata: {str(e)}", "error")
            return False
    
    def assess_quality(self) -> bool:
        """Kalite değerlendirmesi ve finalizasyon"""
        try:
            self.add_status_log("🔍 Kalite değerlendirmesi başlatılıyor...", "info")
            
            generation_data = st.session_state.workflow_state.get('generation_data', {})
            analysis_data = st.session_state.workflow_state.get('analysis_data', {})
            
            image_path = generation_data.get('image_path', '')
            prompt = analysis_data.get('visual_summary', 'AI generated content')
            
            # Kalite değerlendirmesi
            quality_result = self.client.assess_image_quality(image_path, prompt)
            
            if quality_result.get('error'):
                self.add_status_log(f"⚠️ Kalite değerlendirmesi hatası: {quality_result['error']}", "warning")
                quality_score = 0.7  # Varsayılan skor
            else:
                quality_assessment = quality_result.get('quality_assessment', {})
                overall_score = quality_assessment.get('overall_score', {})
                quality_score = overall_score.get('overall_score', 0.7)
                
                self.add_status_log(f"📊 Kalite skoru: {quality_score:.2f}", "info")
            
            # İçerik finalizasyonu
            self.add_status_log("🏷️ İçerik finalize ediliyor...", "info")
            
            finalize_result = self.client.finalize_content(
                image_path=image_path,
                original_prompt=prompt,
                style="modern",
                platform="instagram",
                max_hashtags=15
            )
            
            if finalize_result.get('error'):
                self.add_status_log(f"❌ Finalizasyon hatası: {finalize_result['error']}", "error")
                return False
            else:
                # Final output hazırla
                final_output = {
                    'image_data': generation_data,
                    'quality_data': quality_result,
                    'finalized_content': finalize_result,
                    'quality_score': quality_score
                }
                
                st.session_state.workflow_state['quality_data'] = quality_result
                st.session_state.workflow_state['final_output'] = final_output
                st.session_state.workflow_state['step'] = 4
                
                hashtag_count = len(finalize_result.get('finalized_content', {}).get('hashtags', []))
                self.add_status_log(f"✅ İçerik hazır! {hashtag_count} hashtag oluşturuldu", "success")
                self.add_status_log("🎉 Yayınlamaya hazır!", "success")
                
                return True
                
        except Exception as e:
            self.add_status_log(f"❌ Kalite değerlendirmesi sırasında hata: {str(e)}", "error")
            return False
    
    def get_current_step(self) -> int:
        """Mevcut workflow step'ini al"""
        return st.session_state.workflow_state.get('step', 0)
    
    def get_workflow_data(self, key: str) -> Any:
        """Workflow verisini al"""
        return st.session_state.workflow_state.get(key)
    
    def is_step_completed(self, step: int) -> bool:
        """Step'in tamamlanıp tamamlanmadığını kontrol et"""
        current_step = self.get_current_step()
        return current_step > step
    
    def is_upload_completed(self) -> bool:
        """Upload step'inin tamamlanıp tamamlanmadığını kontrol et"""
        uploaded_files = st.session_state.workflow_state.get('uploaded_files', [])
        keywords = st.session_state.workflow_state.get('keywords', [])
        return len(uploaded_files) > 0 and len(keywords) > 0

# Global workflow manager instance
@st.cache_resource
def get_workflow_manager():
    return WorkflowManager()
