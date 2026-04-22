from pydantic import BaseModel, Field


class AIAskRequest(BaseModel):
    text: str = Field(min_length=3, max_length=4000)


class AIAskResponse(BaseModel):
    answer: str
