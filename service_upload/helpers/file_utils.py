import os
import uuid
import logging

logger = logging.getLogger(__name__)

UPLOAD_DIR = os.getenv("UPLOAD_TEMP_DIR", "tmp")
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_temp_file(file) -> str:
    """Dosyayı geçici klasöre kaydeder ve path döner"""
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    logger.info(f"Dosya geçici kaydedildi: {file_path}")
    return file_path
