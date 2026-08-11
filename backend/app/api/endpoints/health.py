from fastapi import APIRouter
import psutil

router = APIRouter()


@router.get("/health")
def health_check():
    memory = psutil.virtual_memory()
    return {
        "status": "PASS",
        "neo4j": "DISCONNECTED (In-Memory Fallback)",
        "parser_registry": "ONLINE",
        "pipeline": "ONLINE",
        "memory_usage_pct": memory.percent,
        "cpu_usage_pct": psutil.cpu_percent(interval=None)
    }
