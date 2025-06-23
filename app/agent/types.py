from typing_extensions import TypedDict
from typing_extensions import Annotated

class State(TypedDict, total=False):  # total=False makes all keys optional
    question: str
    query: str
    result: str
    answer: str

class QueryOutput(TypedDict):
    """Generated SQL query."""
    query: Annotated[str, ..., "Syntactically valid SQL query."]
