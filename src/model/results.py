from dataclasses import dataclass
from typing import List


@dataclass
class ResultItem:
    name: str
    ingredients: List[str]
    instructions: str
    

@dataclass
class ResultPage:
    search_query: int
    result_items: List[ResultItem]
