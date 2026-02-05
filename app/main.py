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
    from app.repositories import mongo_repo, neo4j_repo, redis_repo, es_repo
    import time

    start_time = time.time()
    services_status = {}
    overall_healthy = True

    # Check API
    services_status["api"] = {
        "status": "up",
        "latency_ms": 0
    }

    # Check MongoDB
    try:
        mongo_start = time.time()
        mongo_repo.client.admin.command('ping')
        mongo_latency = (time.time() - mongo_start) * 1000
        services_status["mongodb"] = {
            "status": "up",
            "latency_ms": round(mongo_latency, 2),
            "uri": mongo_repo.client.address[0] if mongo_repo.client.address else "unknown"
        }
    except Exception as e:
        overall_healthy = False
        services_status["mongodb"] = {
            "status": "down",
            "error": str(e)
        }

    # Check Neo4j
    try:
        neo4j_start = time.time()
        neo4j_repo.driver.verify_connectivity()
        neo4j_latency = (time.time() - neo4j_start) * 1000
        services_status["neo4j"] = {
            "status": "up",
            "latency_ms": round(neo4j_latency, 2)
        }
    except Exception as e:
        overall_healthy = False
        services_status["neo4j"] = {
            "status": "down",
            "error": str(e)
        }

    # Check Redis
    try:
        redis_start = time.time()
        redis_repo.ping()
        redis_latency = (time.time() - redis_start) * 1000
        services_status["redis"] = {
            "status": "up",
            "latency_ms": round(redis_latency, 2)
        }
    except Exception as e:
        # Redis is optional, don't mark overall as unhealthy
        services_status["redis"] = {
            "status": "down",
            "error": str(e),
            "optional": True
        }

    # Check Elasticsearch
    try:
        es_start = time.time()
        es_repo.client.ping()
        es_latency = (time.time() - es_start) * 1000
        services_status["elasticsearch"] = {
            "status": "up",
            "latency_ms": round(es_latency, 2)
        }
    except Exception as e:
        # Elasticsearch is optional, don't mark overall as unhealthy
        services_status["elasticsearch"] = {
            "status": "down",
            "error": str(e),
            "optional": True
        }

    # Calculate total response time
    total_latency = (time.time() - start_time) * 1000

    return {
        "status": "healthy" if overall_healthy else "degraded",
        "timestamp": time.time(),
        "latency_ms": round(total_latency, 2),
        "services": services_status
    }


# Подключить роутеры
from app.api import blocks, documents, search, versions

app.include_router(blocks.router, prefix="/api/blocks", tags=["blocks"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(versions.router, prefix="/api/versions", tags=["versions"])


# Lifecycle events
from app.services import block_service, search_service, cache_service, version_service


@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске"""
    await block_service.initialize()
    await search_service.initialize()
    await cache_service.initialize()
    await version_service.initialize()
    print("✅ Services initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Очистка при остановке"""
    await block_service.shutdown()
    await search_service.shutdown()
    await cache_service.shutdown()
    await version_service.shutdown()
    print("👋 Services shutdown")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
