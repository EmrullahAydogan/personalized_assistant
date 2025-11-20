from pydantic import BaseModel
from typing import List


class SearchRequest(BaseModel):
    query: str
    num_results: int = 5
    lang: str = "tr"


class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    summary: str
