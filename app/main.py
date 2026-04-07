"""FastAPI application entry point"""
from fastapi import FastAPI
from config import settings

app = FastAPI(
    title="Code Knowledge Graph",
    version="0.1.0",
    debug=settings.debug,
)


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint"""
    return {
        "status": "ok",
        "environment": settings.environment,
    }


@app.get("/")
async def root() -> dict:
    """Root endpoint"""
    return {
        "message": "Code Knowledge Graph API",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
