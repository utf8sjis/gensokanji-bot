from pydantic import BaseModel


class PostedData(BaseModel):
    total: int
    ids: list[str]


class TweetDataItem(BaseModel):
    id: str
    text: str
    images: list[str]


class TweetData(BaseModel):
    tweets: list[TweetDataItem]
