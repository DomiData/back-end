from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from app.schema.chat import ChatMessageResponse
from app.services.chat.agent import (
    _build_message_history,
    _extract_sources_from_messages,
    create_chat_agent,
    run_agent,
)
from app.services.chat.prompts import DISCLAIMER_PT


class TestCreateAgent:
    @patch("app.services.chat.agent.ChatOpenAI")
    def test_creates_agent_without_error(self, mock_llm, prediction_data_dir):
        mock_llm.return_value = MagicMock()
        agent = create_chat_agent("test-key", prediction_data_dir)
        assert agent is not None


class TestExtractSourcesFromMessages:
    def test_empty_messages(self):
        sources = _extract_sources_from_messages([])
        assert len(sources) == 1
        assert sources[0].type == "general_knowledge"

    def test_no_tool_messages(self):
        messages = [
            HumanMessage(content="O que causa dengue?"),
            AIMessage(content="A dengue e causada..."),
        ]
        sources = _extract_sources_from_messages(messages)
        assert len(sources) == 1
        assert sources[0].type == "general_knowledge"

    def test_with_prediction_data_tool_message(self):
        messages = [
            ToolMessage(
                content='{"tipo_fonte": "prediction_data", "detalhe_fonte": "time_series.csv - dengue"}',
                tool_call_id="123",
                name="consultar_tendencia",
            ),
        ]
        sources = _extract_sources_from_messages(messages)
        assert len(sources) == 1
        assert sources[0].type == "prediction_data"
        assert sources[0].detail == "time_series.csv - dengue"

    def test_deduplicates_sources(self):
        tool_msg = ToolMessage(
            content='{"tipo_fonte": "prediction_data", "detalhe_fonte": "time_series.csv"}',
            tool_call_id="123",
            name="consultar_tendencia",
        )
        sources = _extract_sources_from_messages([tool_msg, tool_msg])
        assert len(sources) == 1


class TestBuildMessageHistory:
    def test_builds_from_tuples(self):
        history = [("human", "Oi"), ("ai", "Ola!")]
        messages = _build_message_history(history)
        assert len(messages) == 2
        assert isinstance(messages[0], HumanMessage)
        assert isinstance(messages[1], AIMessage)
        assert messages[0].content == "Oi"

    def test_empty_history(self):
        messages = _build_message_history([])
        assert messages == []


class TestRunAgent:
    @pytest.mark.asyncio
    async def test_returns_response_with_disclaimer(self):
        mock_agent = AsyncMock()
        mock_agent.ainvoke.return_value = {
            "messages": [
                HumanMessage(content="O que causa dengue?"),
                AIMessage(content="A dengue e causada pelo virus DENV."),
            ],
        }

        result = await run_agent(mock_agent, "O que causa dengue?", [])

        assert isinstance(result, ChatMessageResponse)
        assert result.answer == "A dengue e causada pelo virus DENV."
        assert result.disclaimer == DISCLAIMER_PT
        assert len(result.sources) >= 1

    @pytest.mark.asyncio
    async def test_handles_agent_error(self):
        mock_agent = AsyncMock()
        mock_agent.ainvoke.side_effect = Exception("API error")

        result = await run_agent(mock_agent, "teste", [])

        assert isinstance(result, ChatMessageResponse)
        assert "erro" in result.answer.lower()
        assert result.disclaimer == DISCLAIMER_PT

    @pytest.mark.asyncio
    async def test_extracts_sources_from_tool_messages(self):
        mock_agent = AsyncMock()
        mock_agent.ainvoke.return_value = {
            "messages": [
                HumanMessage(content="Tendencia de dengue"),
                ToolMessage(
                    content='{"tipo_fonte": "prediction_data", "detalhe_fonte": "time_series.csv - dengue"}',
                    tool_call_id="1",
                    name="consultar_tendencia",
                ),
                AIMessage(content="A tendencia mostra..."),
            ],
        }

        result = await run_agent(mock_agent, "Tendencia de dengue", [])

        assert any(s.type == "prediction_data" for s in result.sources)
