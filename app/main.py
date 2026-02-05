"""
FastAPI Application Entry Point
Dynamic Content Blocks System
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Dynamic Content Blocks API",
    description="Модульная система для работы со структурированным контентом",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В production настроить конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Dynamic Content Blocks API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint для мониторинга"""
    return {
        "status": "healthy",
        "services": {
            "api": "up",
            # TODO: добавить проверки для Neo4j, MongoDB, Elasticsearch
        }
    }


# TODO: подключить роутеры
# from app.api import blocks, documents, search
# app.include_router(blocks.router, prefix="/api/blocks", tags=["blocks"])
# app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
# app.include_router(search.router, prefix="/api/search", tags=["search"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
