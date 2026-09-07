import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

class Settings:
    PROJECT_NAME: str = "RAG-Based Document Intelligent System"
    VERSION: str = "1.0.0"
    
    # Base paths
    BASE_DIR: Path = PROJECT_ROOT
    DATA_DIR: Path = PROJECT_ROOT / os.getenv("DATA_DIR", "data")
    UPLOAD_DIR: Path = DATA_DIR / "uploads"
    PAGE_CACHE_DIR: Path = DATA_DIR / "page_images"
    INDEX_DIR: Path = DATA_DIR / "indices"
    
    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # Model configuration
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "models/gemini-embedding-001")
    LOCAL_EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    GENERATION_MODEL: str = os.getenv("GENERATION_MODEL", "models/gemini-3.6-flash")
    VISION_MODEL: str = os.getenv("VISION_MODEL", "models/gemini-3.6-flash")
    
    # Retrieval Hyperparameters
    TOP_K_RETRIEVAL: int = int(os.getenv("TOP_K_RETRIEVAL", "6"))
    RERANK_TOP_N: int = int(os.getenv("RERANK_TOP_N", "3"))
    RRF_K: int = 60  # Reciprocal Rank Fusion constant
    
    # Chunking Configuration
    MAX_CHUNK_TOKENS: int = 500
    CHUNK_OVERLAP_TOKENS: int = 50
    
    # Server configuration
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "127.0.0.1")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))

settings = Settings()

# Ensure directories exist
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.PAGE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
settings.INDEX_DIR.mkdir(parents=True, exist_ok=True)
