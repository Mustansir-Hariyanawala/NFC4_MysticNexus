#!/usr/bin/env python3
"""
Setup script for the RAG-powered FastAPI Chat System
This script helps you set up the complete system on your friend's GPU PC.
"""

import subprocess
import sys
import os
import requests
import time
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return None

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor} is compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor} is not compatible. Need Python 3.8+")
        return False

def install_python_packages():
    """Install required Python packages"""
    print("\n📦 Installing Python packages...")
    
    # Install packages from requirements.txt
    result = run_command(
        "pip install -r requirements.txt",
        "Installing packages from requirements.txt"
    )
    
    if result is None:
        print("❌ Failed to install packages. Please run manually:")
        print("pip install -r requirements.txt")
        return False
    
    # Download NLTK data
    print("\n📚 Downloading NLTK data...")
    try:
        import nltk
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        print("✅ NLTK data downloaded successfully")
    except Exception as e:
        print(f"❌ Failed to download NLTK data: {e}")
        return False
    
    return True

def check_ollama_installation():
    """Check if Ollama is installed and running"""
    print("\n🤖 Checking Ollama installation...")
    
    # Check if Ollama is installed
    result = run_command("ollama --version", "Checking Ollama version")
    if result is None:
        print("❌ Ollama is not installed. Please install it from: https://ollama.ai")
        print("   After installation, run: ollama serve")
        return False
    
    print(f"✅ Ollama is installed: {result.strip()}")
    
    # Check if Ollama server is running
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"✅ Ollama server is running with {len(models)} models")
            
            # List available models
            if models:
                print("📋 Available models:")
                for model in models:
                    print(f"   - {model['name']}")
            
            return True
        else:
            print(f"❌ Ollama server returned status {response.status_code}")
            return False
    except requests.RequestException:
        print("❌ Ollama server is not running. Please start it with: ollama serve")
        return False

def install_ollama_models():
    """Install required Ollama models"""
    print("\n🔽 Installing Ollama models...")
    
    models_to_install = ["llama2:7b-chat", "mistral:7b-instruct"]
    
    for model in models_to_install:
        print(f"\n📥 Installing {model}...")
        result = run_command(
            f"ollama pull {model}",
            f"Installing {model}"
        )
        
        if result is None:
            print(f"❌ Failed to install {model}. You can install it manually later:")
            print(f"   ollama pull {model}")
        else:
            print(f"✅ {model} installed successfully")

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = [
        "data/chromadb_collections",
        "logs"
    ]
    
    for directory in directories:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def test_system_components():
    """Test if all system components are working"""
    print("\n🧪 Testing system components...")
    
    # Test ChromaDB
    try:
        import chromadb
        print("✅ ChromaDB import successful")
    except ImportError as e:
        print(f"❌ ChromaDB import failed: {e}")
        return False
    
    # Test sentence-transformers
    try:
        from sentence_transformers import SentenceTransformer
        print("✅ sentence-transformers import successful")
    except ImportError as e:
        print(f"❌ sentence-transformers import failed: {e}")
        return False
    
    # Test LangGraph
    try:
        import langgraph
        print("✅ LangGraph import successful")
    except ImportError as e:
        print(f"❌ LangGraph import failed: {e}")
        return False
    
    # Test FastAPI
    try:
        import fastapi
        print("✅ FastAPI import successful")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    return True

def main():
    """Main setup function"""
    print("🚀 RAG-Powered FastAPI Chat System Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Install Python packages
    if not install_python_packages():
        print("\n❌ Package installation failed. Please fix errors and try again.")
        sys.exit(1)
    
    # Test system components
    if not test_system_components():
        print("\n❌ Component testing failed. Please check package installations.")
        sys.exit(1)
    
    # Check Ollama
    ollama_ready = check_ollama_installation()
    
    if ollama_ready:
        # Install Ollama models
        install_ollama_models()
    
    # Final instructions
    print("\n" + "=" * 50)
    print("🎉 Setup completed!")
    print("\n📋 Next steps:")
    
    if not ollama_ready:
        print("1. Install Ollama from: https://ollama.ai")
        print("2. Start Ollama server: ollama serve")
        print("3. Install models: ollama pull llama2:7b-chat")
    
    print("4. Set up your MongoDB connection in config/mongodb.py")
    print("5. Start the FastAPI server: python main.py")
    print("6. Test the health endpoint: http://localhost:8000/api/health")
    print("7. Test the Ollama health: http://localhost:8000/api/chat/health")
    
    print("\n🔧 API Endpoints:")
    print("- POST /api/chat - Create new chat")
    print("- POST /api/chat/{chat_id}/uploadDoc - Upload document")
    print("- POST /api/chat/{chat_id}/prompt - Send prompt (with optional file)")
    print("- GET /api/chat/health - Check Ollama connection")
    
    print("\n💡 The system uses LOCAL processing:")
    print("- ChromaDB for document storage")
    print("- Ollama for LLM inference")
    print("- sentence-transformers for embeddings")
    print("- No external API keys required!")

if __name__ == "__main__":
    main()
