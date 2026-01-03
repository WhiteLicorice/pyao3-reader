from typing import TypedDict, List, Union

WorkID = Union[int, str]
AuthorList = List[str]

class ChapterData(TypedDict):
    """Represents the structured data for a single fanfiction chapter."""
    index: int # begins at 0
    title: str
    html: str