import os
import logging
import pickle
import io
from typing import Optional, Dict, Any, List
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/drive"]

class GoogleDriveClient:
    def __init__(self, root_folder_name: str = "SourceData"):
        self.root_folder_name = root_folder_name
        self.service = self._authenticate()
        self.folder_id = self._find_root_folder()
        self.download_dir = os.getenv("DOWNLOAD_DIR", "./downloads")
        os.makedirs(self.download_dir, exist_ok=True)

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

    def _find_root_folder(self) -> Optional[str]:
        """SourceData klasörünü bulur, ID döner"""
        query = f"name='{self.root_folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = self.service.files().list(q=query, fields="files(id, name)").execute()
        items = results.get("files", [])

        if items:
            folder_id = items[0]["id"]
            logger.info(f"📂 '{self.root_folder_name}' klasörü bulundu (ID: {folder_id})")
            return folder_id
        else:
            logger.warning(f"📂 '{self.root_folder_name}' klasörü bulunamadı")
            return None

    def list_files(self, folder_id: str = None, mime_types: List[str] = None) -> List[Dict[str, Any]]:
        """Belirli bir klasördeki dosyaları listeler"""
        if folder_id is None:
            folder_id = self.folder_id
            
        if folder_id is None:
            logger.error("Klasör ID bulunamadı")
            return []

        query = f"'{folder_id}' in parents and trashed=false"
        if mime_types:
            mime_query = " or ".join([f"mimeType='{m}'" for m in mime_types])
            query += f" and ({mime_query})"
        
        results = self.service.files().list(
            q=query, 
            fields="files(id, name, mimeType, size, createdTime)"
        ).execute()
        
        files = results.get("files", [])
        logger.info(f"📋 {len(files)} dosya bulundu")
        return files

    def download_file(self, file_id: str, file_name: str) -> str:
        """Dosyayı indirir ve local path döner"""
        request = self.service.files().get_media(fileId=file_id)
        file_path = os.path.join(self.download_dir, file_name)

        with io.FileIO(file_path, "wb") as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    logger.info(f"📥 İndiriliyor: {file_name} - {int(status.progress() * 100)}%")

        logger.info(f"✅ Dosya indirildi: {file_name}")
        return file_path

    def get_file_info(self, file_id: str) -> Dict[str, Any]:
        """Dosya bilgilerini getirir"""
        file_info = self.service.files().get(
            fileId=file_id,
            fields="id, name, mimeType, size, createdTime, webViewLink, webContentLink"
        ).execute()
        
        return {
            "id": file_info.get("id"),
            "name": file_info.get("name"),
            "mime_type": file_info.get("mimeType"),
            "size": file_info.get("size"),
            "created_time": file_info.get("createdTime"),
            "view_url": file_info.get("webViewLink"),
            "download_url": file_info.get("webContentLink"),
        }

    def search_files(self, query: str, mime_types: List[str] = None) -> List[Dict[str, Any]]:
        """Dosya arama yapar"""
        search_query = f"name contains '{query}' and trashed=false"
        if mime_types:
            mime_query = " or ".join([f"mimeType='{m}'" for m in mime_types])
            search_query += f" and ({mime_query})"
        
        results = self.service.files().list(
            q=search_query,
            fields="files(id, name, mimeType, parents)"
        ).execute()
        
        return results.get("files", [])


# Singleton instance
_drive_client = None

def get_drive_client() -> GoogleDriveClient:
    global _drive_client
    if _drive_client is None:
        _drive_client = GoogleDriveClient()
    return _drive_client
