from src.api.routes.search_service import router as search_router
from src.api.routes.translate_service import router as translate_router
from src.api.routes.health_service import router as health_router
from src.api.models import SearchQuery, Article
from fastapi import APIRouter


api_routers = APIRouter()
api_routers.include_router(search_router, prefix="/search", tags=["PubMed Search"])
api_routers.include_router(translate_router, prefix="/translate", tags=["DeepSeek Translation"])
api_routers.include_router(health_router, prefix="/health", tags=["Server Status"])