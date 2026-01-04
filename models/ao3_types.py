from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Ao3Chapter:
    """Represents a single chapter in an AO3 story."""
    index: int  # 0-indexed
    title: str
    url: str
    html: Optional[str] = None
    markdown: Optional[str] = None

@dataclass
class Ao3Story:
    """Represents the complete AO3 story with metadata and chapters."""
    url: str
    story_id: str
    title: str
    authors: List[str]
    summary: str
    fandoms: List[str]
    relationships: List[str]
    characters: List[str]
    additional_tags: List[str]
    rating: str
    warnings: List[str]
    status: str
    word_count: int
    chapter_count: int
    published: Optional[str]
    updated: Optional[str]
    chapters: List[Ao3Chapter] = field(default_factory=list)

    def get_chapter(self, index: int) -> Optional[Ao3Chapter]:
        if 0 <= index < len(self.chapters):
            return self.chapters[index]
        return None