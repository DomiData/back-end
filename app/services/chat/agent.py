import json
import logging

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from app.schema.chat import ChatMessageResponse, SourceReference
from app.services.chat.prompts import DISCLAIMER_PT, SYSTEM_PROMPT
from app.services.chat.tools import ALL_TOOLS, set_data_dir

logger = logging.getLogger(__name__)


def create_chat_agent(openai_api_key: str, data_dir: str):
    """Create and return a configured langgraph react agent."""
    set_data_dir(data_dir)

    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.3,
        api_key=openai_api_key,
    )

    agent = create_react_agent(
        model=llm,
        tools=ALL_TOOLS,
        prompt=SYSTEM_PROMPT,
    )

    return agent


def _extract_sources_from_messages(messages: list) -> list[SourceReference]:
    """Extract source references from agent response messages."""
    sources = []
    seen = set()

    for msg in messages:
        if not isinstance(msg, ToolMessage):
            continue

        try:
            obs_data = json.loads(msg.content) if isinstance(msg.content, str) else {}
        except (json.JSONDecodeError, TypeError):
            obs_data = {}

        source_type = obs_data.get("tipo_fonte", "general_knowledge")
        detail = obs_data.get("detalhe_fonte", msg.name or "")

        key = (source_type, detail)
        if key not in seen:
            seen.add(key)
            sources.append(SourceReference(type=source_type, detail=detail))

    if not sources:
        sources.append(SourceReference(
            type="general_knowledge",
            detail="Conhecimento geral do modelo",
        ))

    return sources


def _build_message_history(chat_history: list) -> list:
    """Convert tuple-based chat history to LangChain message objects."""
    messages = []
    for role, content in chat_history:
        if role == "human":
            messages.append(HumanMessage(content=content))
        elif role == "ai":
            messages.append(AIMessage(content=content))
    return messages


async def run_agent(
    agent,
    message: str,
    chat_history: list,
) -> ChatMessageResponse:
    """Run the agent with a message and return a structured response."""
    try:
        history_messages = _build_message_history(chat_history)
        input_messages = history_messages + [HumanMessage(content=message)]

        result = await agent.ainvoke({"messages": input_messages})

        response_messages = result.get("messages", [])

        # Find the last AI message as the answer
        answer = "Desculpe, nao consegui processar sua pergunta."
        for msg in reversed(response_messages):
            if isinstance(msg, AIMessage) and msg.content:
                answer = msg.content
                break

        sources = _extract_sources_from_messages(response_messages)

    except Exception as e:
        logger.error("Agent execution error: %s", e)
        answer = (
            "Desculpe, ocorreu um erro ao processar sua pergunta. "
            "Por favor, tente novamente."
        )
        sources = []

    return ChatMessageResponse(
        answer=answer,
        sources=sources,
        disclaimer=DISCLAIMER_PT,
    )
