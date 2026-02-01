import pytest
from pydantic import ValidationError

from app.schema.chat import ChatMessageRequest, ChatMessageResponse, SourceReference


class TestChatMessageRequest:
    def test_valid_message(self):
        req = ChatMessageRequest(message="O que causa dengue?")
        assert req.message == "O que causa dengue?"

    def test_empty_message_rejected(self):
        with pytest.raises(ValidationError):
            ChatMessageRequest(message="")

    def test_whitespace_only_accepted(self):
        # min_length=1 counts characters, whitespace passes; frontend also validates
        req = ChatMessageRequest(message=" ")
        assert req.message == " "

    def test_long_message_rejected(self):
        with pytest.raises(ValidationError):
            ChatMessageRequest(message="a" * 2001)

    def test_max_length_accepted(self):
        req = ChatMessageRequest(message="a" * 2000)
        assert len(req.message) == 2000


class TestSourceReference:
    def test_valid_source(self):
        src = SourceReference(type="prediction_data", detail="forecast.csv - Dengue")
        assert src.type == "prediction_data"
        assert src.detail == "forecast.csv - Dengue"


class TestChatMessageResponse:
    def test_valid_response(self):
        resp = ChatMessageResponse(
            answer="A dengue e causada pelo virus...",
            sources=[SourceReference(type="general_knowledge", detail="Modelo GPT")],
            disclaimer="Informacao educativa apenas.",
        )
        assert resp.answer == "A dengue e causada pelo virus..."
        assert len(resp.sources) == 1
        assert resp.disclaimer == "Informacao educativa apenas."

    def test_empty_sources(self):
        resp = ChatMessageResponse(
            answer="Resposta",
            sources=[],
            disclaimer="Aviso",
        )
        assert resp.sources == []
