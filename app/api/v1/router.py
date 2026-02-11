from fastapi import APIRouter
from app.api.v1.endpoints import chat, documents, conversations, health

api_v1_router = APIRouter()

api_v1_router.include_router(chat.router, prefix="/chat", tags=["Chat & RAG"])
api_v1_router.include_router(documents.router, prefix="/documents", tags=["Document Management"])
api_v1_router.include_router(conversations.router, prefix="/conversations", tags=["Conversations"])
api_v1_router.include_router(health.router, prefix="/health", tags=["Health & Monitoring"])
