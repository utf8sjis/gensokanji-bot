from pydantic import BaseModel, Field


class PostedData(BaseModel):
    total: int
    ids: list[str]


class TweetData(BaseModel):
    id: str = ""
    text: str = ""
    images: list[str] = Field(default_factory=list)
