"""Minimal FastAPI app for integration testing — only the chat router, no DB/Firebase lifespan."""

from cachetools import TTLCache
from fastapi import FastAPI, HTTPException

import app.api.chat as _chat_module
from app.api.chat import router as chat_router, _get_agent
from app.schema.chat import ChatMessageRequest, ChatMessageResponse
from app.services.chat.agent import run_agent

app = FastAPI()
app.include_router(chat_router)


@app.post("/chat/test-session", response_model=ChatMessageResponse)
async def test_session_message(body: ChatMessageRequest, uid: str = "test-session"):
    """Session-aware test endpoint (no auth). Lives in the test server only."""
    agent = _get_agent()
    chat_history = list(_chat_module._chat_histories.get(uid, []))

    try:
        response = await run_agent(agent, body.message, chat_history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    chat_history.append(("human", body.message))
    chat_history.append(("ai", response.answer))
    if len(chat_history) > 40:
        chat_history = chat_history[-40:]
    _chat_module._chat_histories[uid] = chat_history

    return response


@app.get("/debug/history/{uid}")
async def debug_history(uid: str):
    """Return the current cache state for a given UID (test server only)."""
    history = list(_chat_module._chat_histories.get(uid, []))
    return {"uid": uid, "history": history, "count": len(history)}


@app.delete("/debug/history/{uid}")
async def clear_history(uid: str):
    """Evict a UID from the cache (test server only)."""
    _chat_module._chat_histories.pop(uid, None)
    return {"cleared": uid}


@app.get("/debug/cache-info")
async def cache_info():
    """Return TTLCache metadata."""
    c = _chat_module._chat_histories
    return {
        "type": type(c).__name__,
        "maxsize": c.maxsize,
        "ttl": c.ttl,
        "currsize": c.currsize,
    }


@app.post("/debug/set-ttl")
async def set_cache_ttl(ttl: int):
    """Replace the module-level cache with a new TTLCache at the given TTL (test server only)."""
    _chat_module._chat_histories = TTLCache(maxsize=500, ttl=ttl)
    return {"ttl": ttl}
