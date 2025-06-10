from fastapi import APIRouter

from backend.api.api_v1.endpoints import (
    generic_endpoints,
    llm_endpoints,
    db_endpoints,
)

api_router = APIRouter()

# Generic Endpoints
api_router.include_router(generic_endpoints.router, tags=["Generic"])

# LLM Endpoints
api_router.include_router(llm_endpoints.router, tags=["LLM"])

api_router.include_router(db_endpoints.router, tags=["Database"])
