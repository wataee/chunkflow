import uuid
import json
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from app.api.deps import AuthDependency
from app.config import settings
from app.core.rate_limiter import limiter
from app.schemas.chat import ChatRequest, ChatResponse, ChatMessage, RoleEnum
from app.services.rag_engine import rag_engine
from app.services.cache_service import cache_service

router = APIRouter()


@router.post("", response_model=ChatResponse, summary="Send a chat message with RAG context")
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def chat_endpoint(
    request: Request,
    body: ChatRequest,
    api_key: str = AuthDependency,
):
    conv_id = body.conversation_id or str(uuid.uuid4())
    history = cache_service.get_conversation(conv_id)

    # Save user message to history
    user_msg = ChatMessage(role=RoleEnum.USER, content=body.message)
    cache_service.save_message(conv_id, user_msg)

    # Generate response
    reply, citations, latency_ms = await rag_engine.generate_response(
        query=body.message,
        history=history,
        top_k=body.top_k,
        metadata_filter=body.metadata_filter,
        temperature=body.temperature,
    )

    # Save assistant message with citations to history
    assistant_msg = ChatMessage(role=RoleEnum.ASSISTANT, content=reply, citations=citations)
    cache_service.save_message(conv_id, assistant_msg)

    return ChatResponse(
        conversation_id=conv_id,
        reply=reply,
        citations=citations,
        latency_ms=latency_ms,
        model=settings.LLM_MODEL_NAME,
    )


@router.post("/stream", summary="Stream chat response using Server-Sent Events (SSE)")
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def stream_chat_endpoint(
    request: Request,
    body: ChatRequest,
    api_key: str = AuthDependency,
):
    conv_id = body.conversation_id or str(uuid.uuid4())
    history = cache_service.get_conversation(conv_id)

    # Record user message
    user_msg = ChatMessage(role=RoleEnum.USER, content=body.message)
    cache_service.save_message(conv_id, user_msg)

    async def event_generator():
        yield f"data: {json.dumps({'type': 'start', 'conversation_id': conv_id})}\n\n"
        full_reply = []
        citations_data = []

        async for chunk in rag_engine.stream_response(
            query=body.message,
            history=history,
            top_k=body.top_k,
            metadata_filter=body.metadata_filter,
            temperature=body.temperature,
        ):
            if chunk.get("type") == "token":
                full_reply.append(chunk["delta"])
            elif chunk.get("type") == "citations":
                citations_data = chunk.get("citations", [])
            yield f"data: {json.dumps(chunk)}\n\n"

        # Save completed response to history
        full_text = "".join(full_reply)
        from app.schemas.chat import Citation
        citations = [Citation(**c) for c in citations_data]
        assistant_msg = ChatMessage(role=RoleEnum.ASSISTANT, content=full_text, citations=citations)
        cache_service.save_message(conv_id, assistant_msg)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )
