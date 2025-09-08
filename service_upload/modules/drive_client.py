import os
import logging
import pickle
from typing import Optional, Dict, Any
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

class GoogleDriveClient:
    def __init__(self, root_folder_name: str = "SourceData"):
        self.root_folder_name = root_folder_name
        self.service = self._authenticate()
        self.folder_id = self._ensure_root_folder()

    def _authenticate(self):
        creds = None
        if os.path.exists("token.pickle"):
            with open("token.pickle", "rb") as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials/service-account1.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open("token.pickle", "wb") as token:
                pickle.dump(creds, token)

        logger.info("✅ Google OAuth ile kimlik doğrulama başarılı")
        return build("drive", "v3", credentials=creds)

    def _ensure_root_folder(self) -> str:
        """SourceData klasörünü bulur veya oluşturur, ID döner"""
        query = f"name='{self.root_folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = self.service.files().list(q=query, fields="files(id, name)").execute()
        items = results.get("files", [])

        if items:
            folder_id = items[0]["id"]
            logger.info(f"📂 '{self.root_folder_name}' klasörü bulundu (ID: {folder_id})")
            return folder_id
        else:
            file_metadata = {
                "name": self.root_folder_name,
                "mimeType": "application/vnd.google-apps.folder",
            }
            folder = self.service.files().create(body=file_metadata, fields="id").execute()
            folder_id = folder.get("id")
            logger.info(f"📂 '{self.root_folder_name}' klasörü oluşturuldu (ID: {folder_id})")
            return folder_id

    def upload_file(self, file_path: str, file_name: str) -> Dict[str, Any]:
        """Dosyayı SourceData klasörüne yükler"""
        file_metadata = {"name": file_name, "parents": [self.folder_id]}
        media = MediaFileUpload(file_path, resumable=True)

        uploaded = self.service.files().create(
            body=file_metadata, media_body=media,
            fields="id, webViewLink, webContentLink"
        ).execute()

        logger.info(f"✅ Dosya yüklendi: {file_name} (ID: {uploaded.get('id')})")
        return {
            "id": uploaded.get("id"),
            "view_url": uploaded.get("webViewLink"),
            "download_url": uploaded.get("webContentLink"),
        }


# Singleton instance
_drive_client = None

def get_drive_client() -> GoogleDriveClient:
    global _drive_client
    if _drive_client is None:
        _drive_client = GoogleDriveClient()
    return _drive_client
