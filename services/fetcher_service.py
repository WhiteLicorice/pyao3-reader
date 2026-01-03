import asyncio
from typing import List, Optional
from fanficfare import adapters, configurable
from fanficfare.adapters import base_adapter
from .content_service import ContentService
from models.ao3_types import ChapterData, RawChapter
import html

class FetcherService:
    """Handles interaction with FanFicFare adapters to fetch AO3 data."""

    def __init__(self) -> None:
        """Initializes the FanFicFare configuration with AO3 defaults."""
        self.config = configurable.Configuration(["archiveofourown.org"], "html")
        settings: str = """
[defaults]
is_adult: true
keep_html_attrs: class,id,style
user_agent: pyao3
slow_down_sleep_time: 2
use_view_full_work: true
        """
        self.config.read_string(settings)
        self.adapter: Optional[base_adapter.BaseSiteAdapter] = None
        self.raw_chapters: List[RawChapter] = []

    async def fetch_metadata(self, url: str) -> List[ChapterData]:
        """Initial crawl to get chapter titles and URLs."""
        return await asyncio.to_thread(self._sync_fetch_metadata, url)

    def _sync_fetch_metadata(self, url: str) -> List[ChapterData]:
        self.adapter = adapters.getAdapter(self.config, url)
        self.adapter.extractChapterUrlsAndMetadata()
        self.raw_chapters = self.adapter.get_chapters()
        
        # Return skeleton data (no markdown yet)
        return [
            {
                "index": i,
                "title": html.unescape(c['title']),
                "html": "",
                "markdown": "" # Empty indicates not loaded
            }
            for i, c in enumerate(self.raw_chapters)
        ]

    async def fetch_single_chapter(self, index: int) -> str:
        """Fetch and format a specific chapter on demand."""
        if not self.adapter:
            raise Exception("Adapter not initialized. Call fetch_metadata first.")
        
        return await asyncio.to_thread(self._sync_fetch_chapter, index)

    def _sync_fetch_chapter(self, index: int) -> str:
        chapter_url = self.raw_chapters[index]['url']
        html_string = self.adapter.getChapterTextNum(chapter_url, index)
        return ContentService.clean_html_for_flet(html_string)