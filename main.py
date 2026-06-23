"""FastAPI application entrypoint.

This file defines `app` so `uvicorn main:app` works from project root.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from app.api.upload import router
from app.utils.logger import get_logger

# Load environment variables
load_dotenv()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("=" * 50)
    logger.info("NDA Risk Analyzer API Starting")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"Debug Mode: {os.getenv('DEBUG', 'false')}")
    logger.info("=" * 50)
    yield
    
    # Shutdown
    logger.info("NDA Risk Analyzer API Shutting Down")


app = FastAPI(
    title="NDA Risk Analyzer API",
    version="1.0.0",
    description="AI-Assisted NDA Risk Analysis with Ollama",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    logger.info("Health check request received")
    return {"status": "ok", "service": "NDA Risk Analyzer"}


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "NDA Risk Analyzer API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "upload": "/upload",
            "health": "/health",
        },
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Check logs for details."},
    )


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("API_RELOAD", "true").lower() in ("1", "true", "yes")

    uvicorn.run("main:app", host=host, port=port, reload=reload, log_level="info")
