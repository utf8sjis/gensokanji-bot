from pydantic import BaseModel


class TweetItem(BaseModel):
    id: str
    type: str
    group: str
    text: str
    image_paths: list[str]
