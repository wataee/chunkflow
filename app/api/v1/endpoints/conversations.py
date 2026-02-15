from typing import List
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from app.api.deps import AuthDependency
from app.schemas.conversation import ConversationSummary, ConversationDetail
from app.services.cache_service import cache_service

router = APIRouter()


@router.get("", response_model=List[ConversationSummary], summary="List active conversations")
async def list_conversations(api_key: str = AuthDependency):
    return cache_service.list_conversations()


@router.get("/{conversation_id}", response_model=ConversationDetail, summary="Get full conversation history")
async def get_conversation(conversation_id: str, api_key: str = AuthDependency):
    messages = cache_service.get_conversation(conversation_id)
    if not messages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {conversation_id} not found",
        )
    return ConversationDetail(
        conversation_id=conversation_id,
        messages=messages,
        created_at=messages[0].timestamp,
        updated_at=messages[-1].timestamp,
    )


@router.delete("/{conversation_id}", summary="Delete conversation history")
async def delete_conversation(conversation_id: str, api_key: str = AuthDependency):
    success = cache_service.delete_conversation(conversation_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {conversation_id} not found",
        )
    return {"status": "success", "message": f"Conversation {conversation_id} deleted"}
