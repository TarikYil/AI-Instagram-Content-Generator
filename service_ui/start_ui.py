"""
AI Instagram Content Generator UI Starter
"""
import subprocess
import sys
import os
import time
import requests

def check_service(service_name, port):
    """Servisi kontrol et"""
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=3)
        return response.status_code == 200
    except:
        return False

def check_all_services():
    
    """Tüm servisleri kontrol et"""
    services = {
        "upload": 8001,
        "analysis": 8003, 
        "trend": 8002,
        "generation": 8004,
        "quality": 8005
    }
    
    print("🔍 Checking microservices...")
    all_running = True
    
    for service, port in services.items():
        if check_service(service, port):
            print(f"✅ {service.title()} Service: Running (port {port})")
        else:
            print(f"❌ {service.title()} Service: Not running (port {port})")
            all_running = False
    
    return all_running

def install_requirements():
    """Requirements'ları yükle"""
    try:
        print("📦 Installing requirements...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements!")
        return False

def start_streamlit():
    """Streamlit uygulamasını başlat"""
    try:
        print("🚀 Starting Streamlit UI...")
        print("📱 Opening browser at: http://localhost:8501")
        print("🛑 Press Ctrl+C to stop")
        
        # Streamlit'i başlat
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port=8501",
            "--server.address=0.0.0.0",
            "--browser.gatherUsageStats=false"
        ])
        
    except KeyboardInterrupt:
        print("\n🛑 UI stopped by user")
    except Exception as e:
        print(f"❌ Failed to start UI: {e}")

def main():
    print("🤖 AI Instagram Content Generator - UI Starter")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("app.py"):
        print("❌ app.py not found! Please run this from the service_ui directory.")
        return
    
    
    print("\n" + "=" * 50)
    
    # Check microservices
    services_running = check_all_services()
    
    if not services_running:
        print("\n⚠️  Warning: Some microservices are not running!")
        print("   The UI will start but some features may not work.")
        print("   Please start the required microservices first.")
        
        response = input("\n❓ Do you want to continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("🛑 Cancelled by user")
            return
    
    print("\n" + "=" * 50)
    
    # Start UI
    start_streamlit()

if __name__ == "__main__":
    main()
