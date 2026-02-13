from fastapi import APIRouter
from app.config import settings
from app.db.redis_client import get_cache_client
from app.services.rag_engine import rag_engine

router = APIRouter()


@router.get("/live", summary="Liveness check for container orchestrators")
async def liveness_probe():
    return {"status": "ok", "service": settings.PROJECT_NAME, "version": settings.VERSION}


@router.get("/ready", summary="Readiness check for dependencies")
async def readiness_probe():
    cache_ready = get_cache_client().ping()
    db_configured = bool(settings.POSTGRES_HOST and settings.POSTGRES_DB)
    vector_ready = rag_engine._vector_store is not None

    status_str = "ready" if (cache_ready and db_configured) else "degraded"

    return {
        "status": status_str,
        "components": {
            "cache": "operational" if cache_ready else "offline",
            "database_config": "configured" if db_configured else "missing",
            "vector_store": "connected" if vector_ready else "standalone_mode",
        },
        "version": settings.VERSION,
    }
