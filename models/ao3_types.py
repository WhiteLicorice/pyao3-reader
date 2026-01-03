from typing import TypedDict

type WorkID = int | str
type AuthorList = list[str]

class ChapterData(TypedDict):
    index: int
    title: str
    html: str