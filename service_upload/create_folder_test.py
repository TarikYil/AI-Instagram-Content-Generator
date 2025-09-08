"""
Google Drive'da test klasörü oluşturma
"""

import requests

BASE_URL = "http://localhost:8001"

def create_test_folder():
    """Test klasörü oluştur"""
    print("📁 Test klasörü oluşturuluyor...")
    
    response = requests.post(
        f"{BASE_URL}/upload/folder",
        params={
            "folder_name": "AI_Instagram_Content_Upload_Test",
            "parent_folder_id": None  # Ana klasörde oluştur
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Test klasörü oluşturuldu!")
        print(f"📋 Klasör ID: {result['folder_id']}")
        print(f"📂 Klasör Adı: {result['folder_name']}")
        print(f"\n🔗 Bu ID'yi folder_id olarak kullanabilirsiniz: {result['folder_id']}")
        return result['folder_id']
    else:
        print(f"❌ Klasör oluşturulamadı: {response.status_code}")
        print(response.text)
        return None

if __name__ == "__main__":
    folder_id = create_test_folder()
    if folder_id:
        print(f"\n💡 Artık bu folder_id'yi kullanabilirsiniz: {folder_id}")
