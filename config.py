"""
Configuration module for NDA Risk Analyzer.

Loads environment variables and provides configuration defaults.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Base configuration"""
    
    # API Configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 8000))
    API_RELOAD = os.getenv("API_RELOAD", "true").lower() == "true"
    API_WORKERS = int(os.getenv("API_WORKERS", 1))
    
    # LLM Configuration
    LLM_MODEL = os.getenv("LLM_MODEL", "gemma:2b")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", 0))
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434")

    # Local OCR Configuration
    TESSERACT_CMD = os.getenv("TESSERACT_CMD", "")
    OCR_LANGUAGE = os.getenv("OCR_LANGUAGE", "eng")
    OCR_DPI = int(os.getenv("OCR_DPI", 300))
    
    # Clause Processing
    MAX_CLAUSES = int(os.getenv("MAX_CLAUSES", 20))
    MIN_CLAUSE_LENGTH = int(os.getenv("MIN_CLAUSE_LENGTH", 50))
    MAX_CLAUSE_LENGTH = int(os.getenv("MAX_CLAUSE_LENGTH", 2000))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR = os.getenv("LOG_DIR", "logs")
    
    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"
    
    @classmethod
    def to_dict(cls):
        """Convert config to dictionary"""
        return {
            key: getattr(cls, key)
            for key in dir(cls)
            if not key.startswith("_") and key.isupper()
        }


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    API_RELOAD = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    API_RELOAD = False
    API_WORKERS = 4


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True


# Select configuration based on environment
def get_config():
    """Get configuration based on ENVIRONMENT variable"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionConfig
    elif env == "testing":
        return TestingConfig
    else:
        return DevelopmentConfig
