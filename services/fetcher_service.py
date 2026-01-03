import asyncio
from typing import List
from fanficfare import adapters, configurable # type: ignore
from fanficfare.adapters import base_adapter # type: ignore
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

    async def fetch_formatted_chapters(self, url: str) -> List[ChapterData]:
        """Asynchronously fetches and pre-processes chapters."""
        # We run the whole sync block in a thread to keep the UI responsive
        return await asyncio.to_thread(self._sync_fetch, url)

    def _sync_fetch(self, url: str) -> List[ChapterData]:
        adapter: base_adapter.BaseSiteAdapter = adapters.getAdapter(self.config, url)
        adapter.extractChapterUrlsAndMetadata()
        
        fetched_chapters: list[RawChapter] = adapter.get_chapters()
        chapters_data: List[ChapterData] = []
        
        for i, chapter in enumerate(fetched_chapters):
            # The raw string as is in HTML.
            html_string: str = adapter.getChapterTextNum(chapter['url'], i)
            
            # Convert to Markdown HERE, in the background thread.
            # This prevents the UI from stuttering when rendering large chapters.
            # Automatically unescapes.
            md_content: str = ContentService.clean_html_for_flet(html_string)
            
            chapters_data.append({
                "index": i,
                "title": html.unescape(chapter['title']),
                "html": html_string,
                "markdown": md_content
            })
            
        return chapters_data