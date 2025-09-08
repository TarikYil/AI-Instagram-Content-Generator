## AI Instagram Content Generator

End-to-end, multi-agent pipeline that analyzes trends and input materials, generates Instagram-ready visuals and captions, evaluates quality, and prepares a final publishable package. The system is composed of multiple FastAPI microservices orchestrated by a Streamlit web UI.

<img width="1907" height="904" alt="image" src="https://github.com/user-attachments/assets/35842fe8-e284-475f-b454-8f0227d1d2fc" />

### Key Capabilities
- Trend analysis and hashtag suggestion
- Visual/text analysis of uploaded materials
- AI-based image generation (Stable Diffusion family)
- Quality assessment with CLIP/aesthetic scoring and finalization
- Google Drive integration for asset handling

### Architecture Overview
- `service_ui` (Streamlit, Orchestrator & Dashboard)
- `service_trend` (FastAPI, Trend analysis)
- `service_analysis` (FastAPI, Material/content analysis)
- `service_generation` (FastAPI, AI content generation)
- `service_quality` (FastAPI, Quality assessment & finalization)
- `service_upload` (FastAPI, Google Drive upload and file management)


Each service exposes a `/health` endpoint and an optional `/docs` (Swagger) UI for local development.

### Data Flow (High Level)
1) Upload materials (images/videos/text/keywords) in the UI → `service_upload` stores and shares references.
2) Start processing → `service_trend` returns platform trends and hashtags; `service_analysis` analyzes uploaded materials.
3) Generate content → `service_generation` produces an image based on style and analysis/trend context.
4) Quality assessment → `service_quality` scores and finalizes content (caption + hashtags + score).
5) UI bundles the final output for download and publishing.

---

## Services

### 1) service_ui (Streamlit)
- Path: `service_ui/`
- Entry: `app.py`
- Purpose: Orchestrates the workflow, shows live status, previews generated output, and exposes controls for each step.
- Start (dev):
```bash
cd service_ui
pip install -r requirements.txt
streamlit run app.py
```

### 2) service_trend (FastAPI)
- Path: `service_trend/`
- Entry: `main.py`
- Default port: 8002
- Purpose: Provides trend insights (e.g., YouTube/Instagram) and hashtag suggestions.
- Start (dev):
```bash
cd service_trend
pip install -r requirements.txt
python main.py
```

### 3) service_analysis (FastAPI)
- Path: `service_analysis/`
- Entry: `main.py`
- Default port: 8003
- Purpose: Fetches files (e.g., from Drive) and runs AI analysis on visuals/text (keywords, visual summaries, etc.).
- Start (dev):
```bash
cd service_analysis
pip install -r requirements.txt
python main.py
```

### 4) service_generation (FastAPI)
- Path: `service_generation/`
- Entry: `main.py`
- Default port: 8004
- Purpose: Generates images using Stable Diffusion-based pipelines, with multiple style presets.
- Start (dev):
```bash
cd service_generation
pip install -r requirements.txt
python main.py
```

### 5) service_quality (FastAPI)
- Path: `service_quality/`
- Entry: `main.py`
- Default port: 8005
- Purpose: Rates text-to-image alignment and visual quality; finalizes caption/hashtags.
- Start (dev):
```bash
cd service_quality
pip install -r requirements.txt
python main.py
```

### 6) service_upload (FastAPI)
- Path: `service_upload/`
- Entry: `main.py`
- Default port: 8001
- Purpose: Uploads and manages files on Google Drive; provides links/metadata to other services.
- Docs: See `service_upload/README.md` for endpoints and configuration details.
- Start (dev):
```bash
cd service_upload
pip install -r requirements.txt
python main.py
```

---

## Technologies
- Programming Language: Python (3.10+ recommended)
- Web UI: Streamlit
- API Framework: FastAPI (per microservice)
- Models: Stable Diffusion (image generation), CLIP (similarity/quality), BLIP (vision-language analysis), aesthetic scoring models
- Data: Google Drive (asset storage), local temp storage
- Orchestration: Simple REST calls from UI to microservices
- Optional: CUDA-enabled GPU for faster generation; CPU fallback available

---

## Models & AI Components
- Stable Diffusion / Diffusion-based generators (via `service_generation/helpers`)
- CLIP-based scoring for text–image alignment (in `service_quality`)
- BLIP or similar VLMs for visual summaries/keywords (in `service_analysis`)
- Aesthetic scoring to estimate perceived image quality

Note: Exact weights/backends can be swapped behind the helper interfaces.

---

## How the System Works
1) Upload: Users upload files and provide keywords/description in the UI.
2) Process: The UI triggers trend + analysis services; results are displayed (trends, hashtags, visual summaries, keywords).
3) Generate: Users pick a style; the generation service returns an image accessible via the UI.
4) Quality: The quality service rates and finalizes content (caption + hashtags + quality score).
5) Final Output: The UI packages the output, lets users download the image and copy captions/hashtags.

---

## Running Locally

### Prerequisites
- Python 3.10+ and pip
- (Optional) NVIDIA GPU with CUDA for faster image generation
- Google Drive credentials for upload/analysis services when Drive access is required

### Start All Services from Project Root (single command)
From the repository root:
```bash
python start_all.py
```
This launches: Upload (8001), Trend (8002), Analysis (8003), Generation (8004), Quality (8005), and UI (8501). Press Ctrl+C to stop all.

### Start All Services (manually, dev)
Open separate terminals and run each service as shown in the Services section. Then start the UI:
```bash
cd service_ui
pip install -r requirements.txt
streamlit run app.py
```
Default UI is available on `http://localhost:8501`.

### Docker
Each microservice includes a `Dockerfile`. A sample `docker-compose.yml` for `service_upload` is available under the service directory. You can create a top-level compose file to orchestrate all services as needed for your environment.

---

## Configuration

### Common
- All services expose `/health` for health checks and optional `/docs` for Swagger UI in dev.
- Ports (default): UI (8501), Trend (8002), Analysis (8003), Generation (8004), Quality (8005), Upload (8001)

### Google Drive (service_upload, service_analysis)
- Place your service account JSON under `credentials/` and point the service to it (see per-service README/ENV).
- Example environment variables (`service_upload`):
```bash
SERVICE_NAME=service_upload
SERVICE_VERSION=1.0.0
HOST=0.0.0.0
PORT=8001
DEBUG=false
GOOGLE_CREDENTIALS_PATH=./credentials/service-account.json
GOOGLE_DRIVE_FOLDER_ID=your_folder_id
MAX_FILE_SIZE=52428800
ALLOWED_EXTENSIONS=.jpg,.jpeg,.png,.gif,.webp,.pdf,.doc,.docx,.txt,.mp4,.mp3,.wav,.zip,.json,.csv
ALLOWED_ORIGINS=*
```

---

## API Notes
- Health: `GET /health` on each service returns a simple status payload.
- Docs: `GET /docs` (dev) opens Swagger UI to explore endpoints.
- Upload examples and full endpoint list are documented in `service_upload/README.md`.

---

## Security & Reliability
- Service account authentication for Google APIs
- File size/type validation and CORS configuration
- Optional resource limits in container environments
- Health checks and structured logging

---

## Development Tips
- Use virtual environments per service: `python -m venv venv && source venv/bin/activate` (Windows: `venv\Scripts\activate`).
- Install per-service dependencies from their `requirements.txt`.
- For faster iteration, run services with auto-reload (`uvicorn` reload or `streamlit` hot-reload).

---

## License
Add your preferred license here.

## Acknowledgements
- Stable Diffusion, CLIP, BLIP and related open-source communities.


#

