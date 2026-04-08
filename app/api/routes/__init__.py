from fastapi import APIRouter

from app.api.routes.repos import router as repos_router

api_router = APIRouter()
api_router.include_router(repos_router)
