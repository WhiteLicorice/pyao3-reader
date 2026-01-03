from typing import TypedDict, List, Union

WorkID = Union[int, str]
AuthorList = List[str]

class ChapterData(TypedDict):
    """Represents the structured data for a single fanfiction chapter."""
    index: int  # 0-indexed
    title: str
    html: str
    markdown: str  # Pre-processed for the UI