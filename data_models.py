from pydantic import BaseModel


class PostedData(BaseModel):
    total: int
    ids: list[int]
