from pydantic import BaseModel, Field


class PostedData(BaseModel):
    total: int
    ids: list[str]


class TweetDataItem(BaseModel):
    id: str = ""
    text: str = ""
    images: list[str] | None = Field(default_factory=list)


class TweetData(BaseModel):
    tweets: list[TweetDataItem]
