"""
AI Instagram Content Generator - Streamlit UI
Multi-Agent Content Pipeline Dashboard
"""
import streamlit as st
import time
from typing import List
from PIL import Image
import io

# Local imports
from utils.workflow_manager import get_workflow_manager
from services.microservice_client import get_microservice_client

# Page config
st.set_page_config(
    page_title="AI Instagram Content Generator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide progress bar completely
st.markdown("""
<script>
const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
        const progressBars = document.querySelectorAll('[data-testid="stProgress"]');
        progressBars.forEach(function(bar) {
            bar.style.display = 'none';
        });
    });
});
observer.observe(document.body, { childList: true, subtree: true });
</script>
""", unsafe_allow_html=True)

# Custom CSS
st.markdown("""
<style>
/* Hide progress bars */
.stProgress > div > div > div > div {
    display: none;
}

/* Hide top progress bar */
.main .block-container {
    padding-top: 1rem;
}

/* Hide Streamlit's default progress indicator */
.stApp > header {
    display: none;
}

/* Hide running indicator */
.stAppViewContainer > .main > .block-container > .stProgress {
    display: none;
}

/* Hide all progress elements */
div[data-testid="stProgress"] {
    display: none !important;
}

.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    text-align: center;
    color: #1f77b4;
    margin-bottom: 2rem;
}

.step-container {
    border: 2px solid #e0e0e0;
    border-radius: 10px;
    padding: 1rem;
    margin: 1rem 0;
    background-color: #f9f9f9;
}

.step-active {
    border-color: #1f77b4;
    background-color: #e3f2fd;
}

.step-completed {
    border-color: #4caf50;
    background-color: #e8f5e8;
}

.status-log {
    background-color: #f5f5f5;
    padding: 0.5rem;
    border-radius: 5px;
    margin: 0.25rem 0;
    font-family: monospace;
}

.status-success { color: #4caf50; }
.status-error { color: #f44336; }
.status-warning { color: #ff9800; }
.status-info { color: #2196f3; }

.preview-container {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 1rem;
    background-color: white;
}

.final-output {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem;
    border-radius: 15px;
    text-align: center;
    margin: 2rem 0;
}
</style>
""", unsafe_allow_html=True)

def main():
    # Initialize session state first
    if 'workflow_state' not in st.session_state:
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
    
    # Initialize workflow manager
    workflow_manager = get_workflow_manager()
    client = get_microservice_client()
    
    # Header
    st.markdown('<h1 class="main-header">AI Instagram Content Generator</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666; font-size: 1.2rem;">Multi-Agent Content Pipeline</p>', unsafe_allow_html=True)
    
    # Sidebar - Service Health Check
    with st.sidebar:
        st.header("Service Status")
        
        if st.button("Check Services", type="secondary"):
            health_status = workflow_manager.check_services_health()
            
            for service, status in health_status.items():
                if status:
                    st.success(f"{service.title()}: Online")
                else:
                    st.error(f"{service.title()}: Offline")
        
        st.divider()
        
        # Workflow Progress
        st.header("Progress")
        current_step = workflow_manager.get_current_step()

        steps = ["Upload", "Process", "Generate", "Quality"]
        for i, step in enumerate(steps):
            if i < current_step:
                st.success(f"{step} ✓")
            elif i == current_step:
                st.info(f"{step} ⏳")
            else:
                st.text(f"{step} ⏸️")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Step 1: File Upload
        with st.container():
            step_class = "step-container"
            if current_step == 0:
                step_class += " step-active"
            elif current_step > 0:
                step_class += " step-completed"
            
            st.markdown(f'<div class="{step_class}">', unsafe_allow_html=True)
            st.subheader("Step 1: Upload Materials")
            
            uploaded_files = st.file_uploader(
                "Upload your content materials",
                type=['jpg', 'jpeg', 'png', 'mp4', 'avi', 'mov'],
                accept_multiple_files=True,
                help="Upload images, videos, or other content materials"
            )
            
            # Preview uploaded files
            if uploaded_files:
                st.write(f"**Uploaded Files ({len(uploaded_files)}):**")
                
                # Create columns for preview
                cols = st.columns(min(len(uploaded_files), 4))  # Max 4 columns
                
                for i, uploaded_file in enumerate(uploaded_files):
                    col_idx = i % 4
                    with cols[col_idx]:
                        st.write(f"**{uploaded_file.name}**")
                        
                        # Check file type
                        if uploaded_file.type.startswith('image/'):
                            # Show image preview
                            try:
                                image = Image.open(uploaded_file)
                                st.image(image, width=150, caption=f"Size: {uploaded_file.size} bytes")
                            except Exception as e:
                                st.error(f"Cannot preview: {e}")
                        elif uploaded_file.type.startswith('video/'):
                            # Show video info
                            st.video(uploaded_file)
                            st.caption(f"Size: {uploaded_file.size} bytes")
                        else:
                            st.info(f"File type: {uploaded_file.type}")
                            st.caption(f"Size: {uploaded_file.size} bytes")
            
            col_a, col_b = st.columns(2)
            with col_a:
                keywords_input = st.text_input(
                    "Keywords (comma separated)",
                    placeholder="gaming, RGB, setup, streaming"
                )
            
            with col_b:
                description_input = st.text_area(
                    "Content Description",
                    placeholder="Describe your content...",
                    height=100
                )
            
            # Upload button
            upload_disabled = not uploaded_files or not keywords_input
            if st.button("Upload Materials", disabled=upload_disabled, type="primary"):
                keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]
                
                with st.spinner("Uploading materials..."):
                    success = workflow_manager.upload_materials(uploaded_files, keywords, description_input)
                    if success:
                        st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Step 2: Start Process
        with st.container():
            step_class = "step-container"
            if current_step == 1:
                step_class += " step-active"
            elif current_step > 1:
                step_class += " step-completed"
            
            st.markdown(f'<div class="{step_class}">', unsafe_allow_html=True)
            st.subheader("Step 2: Start Process")
            st.write("Analyze trends and process uploaded materials")
            
            # Process button logic - sadece dosya yüklenmiş mi kontrol et
            uploaded_files = st.session_state.workflow_state.get('uploaded_files', [])
            keywords = st.session_state.workflow_state.get('keywords', [])
            process_disabled = len(uploaded_files) == 0 or len(keywords) == 0
            
            if st.button("Start Process", disabled=process_disabled, type="primary"):
                with st.spinner("Processing trends and materials..."):
                    success = workflow_manager.start_process()
                    if success:
                        st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Step 3: Generate Content
        with st.container():
            step_class = "step-container"
            if current_step == 2:
                step_class += " step-active"
            elif current_step > 2:
                step_class += " step-completed"
            
            st.markdown(f'<div class="{step_class}">', unsafe_allow_html=True)
            st.subheader("Step 3: Generate Content")
            
            # Style selection
            styles_result = client.get_generation_styles()
            if not styles_result.get('error'):
                available_styles = list(styles_result.get('available_styles', {}).keys())
                selected_style = st.selectbox(
                    "Choose Generation Style",
                    options=available_styles,
                    index=0 if available_styles else None
                )
            else:
                selected_style = "modern"
            
            generate_disabled = current_step < 2
            if st.button("Generate Image", disabled=generate_disabled, type="primary"):
                with st.spinner("Generating content..."):
                    success = workflow_manager.generate_content(selected_style)
                    if success:
                        st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Step 4: Quality Assessment
        with st.container():
            step_class = "step-container"
            if current_step == 3:
                step_class += " step-active"
            elif current_step > 3:
                step_class += " step-completed"
            
            st.markdown(f'<div class="{step_class}">', unsafe_allow_html=True)
            st.subheader("Step 4: Quality Assessment")
            st.write("Evaluate quality and finalize content")
            
            quality_disabled = current_step < 3
            if st.button("Quality Check", disabled=quality_disabled, type="primary"):
                with st.spinner("Assessing quality and finalizing..."):
                    success = workflow_manager.assess_quality()
                    if success:
                        st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Right column - Results and Preview
    with col2:
        # Trend Analysis Results
        trend_data = workflow_manager.get_workflow_data('trend_data')
        if trend_data:
            st.subheader("Trend Analysis")
            
            if trend_data.get('trends'):
                st.write("**YouTube Trends:**")
                for trend in trend_data['trends'][:5]:  # Show first 5
                    st.write(f"• {trend}")
            
            if trend_data.get('hashtags'):
                st.write("**Trending Hashtags:**")
                hashtag_text = ' '.join(trend_data['hashtags'][:8])  # Show first 8
                st.code(hashtag_text)
            
            st.divider()
        
        # Analysis Results
        analysis_data = workflow_manager.get_workflow_data('analysis_data')
        if analysis_data:
            st.subheader("Content Analysis")
            
            if analysis_data.get('visual_summary'):
                st.write("**Visual Summary:**")
                st.write(analysis_data['visual_summary'][:200] + "..." if len(analysis_data['visual_summary']) > 200 else analysis_data['visual_summary'])
            
            if analysis_data.get('keywords'):
                st.write("**Keywords Found:**")
                keywords_text = ', '.join(analysis_data['keywords'][:10])  # Show first 10
                st.code(keywords_text)
            
        # Generated Content Preview (only show when available)
        generation_data = workflow_manager.get_workflow_data('generation_data')
        if generation_data:
            st.divider()
            st.subheader("Generated Content")
            
            st.markdown('<div class="preview-container">', unsafe_allow_html=True)
            
            # Try to download and display image
            filename = generation_data.get('filename')
            if filename:
                try:
                    image_bytes = client.download_generated_image(filename)
                    if image_bytes:
                        image = Image.open(io.BytesIO(image_bytes))
                        st.image(image, caption=f"Generated: {filename}", use_column_width=True)
                except Exception as e:
                    st.error(f"Could not load image: {e}")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Final Output Section
    final_output = workflow_manager.get_workflow_data('final_output')
    if final_output:
        st.markdown('<div class="final-output">', unsafe_allow_html=True)
        st.markdown("# Ready to Publish!")
        
        finalized_content = final_output.get('finalized_content', {}).get('finalized_content', {})
        quality_score = final_output.get('quality_score', 0)
        
        col_final1, col_final2, col_final3 = st.columns(3)
        
        with col_final1:
            st.metric("Quality Score", f"{quality_score:.2f}", delta=None)
        
        with col_final2:
            hashtags = finalized_content.get('hashtags', [])
            st.metric("Hashtags", len(hashtags))
        
        with col_final3:
            st.metric("Status", "Ready")
        
        # Show final content
        if finalized_content:
            st.subheader("Final Caption")
            caption = finalized_content.get('caption', 'No caption generated')
            st.text_area("Caption", value=caption, height=100, disabled=True, label_visibility="collapsed")
            
            st.subheader("Hashtags")
            hashtag_text = ' '.join(hashtags) if hashtags else 'No hashtags generated'
            st.text_area("Hashtags", value=hashtag_text, height=60, disabled=True, label_visibility="collapsed")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Download and Reset buttons
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            # Download button
            generation_data = final_output.get('image_data', {})
            filename = generation_data.get('filename')
            
            if filename:
                try:
                    image_bytes = client.download_generated_image(filename)
                    if image_bytes:
                        st.download_button(
                            label="Download Image",
                            data=image_bytes,
                            file_name=filename,
                            mime="image/png",
                            type="primary"
                        )
                except Exception as e:
                    st.error(f"Download error: {e}")
        
        with col_btn2:
            # Reset workflow button
            if st.button("Start New Workflow", type="secondary"):
                workflow_manager.reset_workflow_state()
                st.rerun()

if __name__ == "__main__":
    main()
