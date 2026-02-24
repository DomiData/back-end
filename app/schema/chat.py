from pydantic import BaseModel, Field


class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)


class SourceReference(BaseModel):
    type: str  # "prediction_data" | "general_knowledge"
    detail: str


class ChatMessageResponse(BaseModel):
    answer: str
    sources: list[SourceReference]
    disclaimer: str
