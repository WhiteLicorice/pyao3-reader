import asyncio
import flet as ft
from typing import List
from fanficfare import adapters, configurable
from models.ao3_types import ChapterData

class FetcherService:
    """Handles interaction with FanFicFare adapters to fetch AO3 data."""

    def __init__(self) -> None:
        """Initializes the FanFicFare configuration with AO3 defaults."""
        self.config = configurable.Configuration(["archiveofourown.org"], "html")
        
        # INI-formatted string for internal ConfigParser
        personal_settings: str = """
[defaults]
is_adult: true
keep_html_attrs: class,id,style
user_agent: pyao3-reader
slow_down_sleep_time: 2
use_view_full_work: true
        """
        self.config.read_string(personal_settings)

    async def fetch_formatted_chapters(self, url: str) -> List[ChapterData]:
        """Asynchronously fetches and formats chapters from a given AO3 URL.

        Args:
            url: The full URL of the AO3 work or chapter.

        Returns:
            A list of ChapterData dictionaries containing titles and HTML content.
        """
        return await asyncio.to_thread(self._sync_fetch, url)

    def _sync_fetch(self, url: str) -> List[ChapterData]:
        """Synchronous internal method to handle the FanFicFare adapter lifecycle.
ao3_types
        Args:
            url: The URL to fetch.

        Returns:
            List of processed chapters.
        """
        adapter = adapters.getAdapter(self.config, url)
        adapter.extractChapterUrlsAndMetadata()
        
        fetched_chapters = adapter.get_chapters()
        chapters_data: List[ChapterData] = []
        
        for i, chapter in enumerate(fetched_chapters):
            # adapter.get_chapters() returns objects that support dict-like access
            chapter_url: str = chapter['url']
            chapter_title: str = chapter['title']
            
            # getChapterTextNum is the OTW-specific method for content retrieval
            chapter_html: str = adapter.getChapterTextNum(chapter_url, i)
            
            chapters_data.append({
                "index": i + 1,
                "title": chapter_title,
                "html": chapter_html
            })
            
        return chapters_data