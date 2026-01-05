import asyncio
import html
from typing import Optional

from fanficfare import adapters
from fanficfare.configurable import Configuration
from fanficfare.adapters.base_adapter import BaseSiteAdapter
from fanficfare.story import Story

from services.content_service import ContentService
from models.ao3_types import Ao3Story, Ao3Chapter
from constants import AO3_DEFAULTS

class FetcherService:
    """Handles interaction with FanFicFare adapters to fetch AO3 data."""

    def __init__(self) -> None:
        """Initializes the FanFicFare configuration with AO3 defaults."""
        self.config = Configuration(["archiveofourown.org"], "html")
        settings = AO3_DEFAULTS
        self.config.read_string(settings) # magic method, ugh
        self.adapter: Optional[BaseSiteAdapter] = None
        self.story: Optional[Ao3Story] = None

    async def fetch_story(self, url: str) -> Ao3Story:
        """Crawl the story to extract full metadata and chapter list."""
        return await asyncio.to_thread(self._sync_fetch_story, url)

    def _sync_fetch_story(self, url: str) -> Ao3Story:
        self.adapter = adapters.getAdapter(self.config, url)
        # This performs the network request and parses the metadata page
        # Need to hot load adapter
        self.adapter.extractChapterUrlsAndMetadata()
        
        fff_story: Story = self.adapter.story
        
        def _split_meta(self, key: str) -> list[str]:
            val = fff_story.getMetadata(key)
            return [item.strip() for item in val.split(',')] if val else []
    
        # Extract metadata using FFF keys
        # FFF maps AO3 fields to these specific internal keys
        # TODO: Validate this.
        self.story = Ao3Story(
            url=url,
            story_id=fff_story.getMetadata('storyId'),
            title=html.unescape(fff_story.getMetadata('title')),
            authors=fff_story.getMetadata('author'),
            summary=fff_story.getMetadata('description'),
            fandoms=fff_story.getMetadata('category'),
            relationships=fff_story.getMetadata('ships'),
            characters=fff_story.getMetadata('characters'),
            additional_tags=fff_story.getMetadata('genre'),
            rating=fff_story.getMetadata('rating'),
            warnings=fff_story.getMetadata('warnings'),
            status=fff_story.getMetadata('status'),
            word_count=int(fff_story.getMetadata('numWords').replace(',', '') or 0),
            chapter_count=int(fff_story.getMetadata('numChapters') or 0),
            published=fff_story.getMetadata('datePublished'),
            updated=fff_story.getMetadata('dateUpdated'),
            chapters=[
                Ao3Chapter(
                    index=i,
                    title=html.unescape(c['title']),
                    url=c['url']
                )
                for i, c in enumerate(self.adapter.get_chapters())
            ]
        )
        return self.story

    async def fetch_chapter_content(self, index: int) -> str:
        """Fetch and format a specific chapter on demand, updating the story object."""
        if not self.adapter or not self.story:
            raise Exception("Adapter not initialized. Call fetch_story first.")
        
        chapter = self.story.get_chapter(index)
        if not chapter:
            raise IndexError(f"Chapter index {index} out of range.")

        if not chapter.markdown:
            markdown = await asyncio.to_thread(self._sync_fetch_chapter_body, chapter.url, index)
            chapter.markdown = markdown
            
        return chapter.markdown

    def _sync_fetch_chapter_body(self, url: str, index: int) -> str:
        # FanFicFare provides the raw HTML via getChapterTextNum
        html_string = self.adapter.getChapterTextNum(url, index)
        return ContentService.clean_html_for_flet(html_string)