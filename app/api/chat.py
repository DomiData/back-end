import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.core.config import settings
from app.core.security import get_firebase_claims
from app.schema.chat import ChatMessageRequest, ChatMessageResponse
from app.services.chat.agent import create_chat_agent, run_agent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])

_agent: Any = None
_chat_histories: dict[str, list] = {}


def _get_agent():
    global _agent
    if _agent is None:
        if not settings.OPENAI_API_KEY:
            raise HTTPException(
                status_code=503,
                detail="Chat service is not configured. OPENAI_API_KEY is missing.",
            )
        _agent = create_chat_agent(
            openai_api_key=settings.OPENAI_API_KEY,
            data_dir=settings.PREDICTION_DATA_DIR,
        )
    return _agent


@router.post("/message", status_code=200, response_model=ChatMessageResponse)
async def send_message(
    body: ChatMessageRequest,
    claims: dict = Depends(get_firebase_claims),
):
    agent = _get_agent()

    uid = claims.get("uid", "anonymous")
    if uid not in _chat_histories:
        _chat_histories[uid] = []

    chat_history = _chat_histories[uid]

    try:
        response = await run_agent(agent, body.message, chat_history)
    except Exception as e:
        logger.error("Chat error for user %s: %s", uid, e)
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao processar a mensagem. Tente novamente.",
        ) from e

    # Update in-memory history (keep last 20 exchanges)
    chat_history.append(("human", body.message))
    chat_history.append(("ai", response.answer))
    if len(chat_history) > 40:
        _chat_histories[uid] = chat_history[-40:]

    return response


# Temporary test endpoint - remove in production
@router.post("/test", status_code=200, response_model=ChatMessageResponse)
async def test_message(body: ChatMessageRequest):
    """Test endpoint without authentication - for development only."""
    agent = _get_agent()
    response = await run_agent(agent, body.message, [])
    return response
