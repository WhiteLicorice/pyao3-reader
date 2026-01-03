import asyncio
from fanficfare import adapters, configurable
from models.ao3_types import ChapterData

class FetcherService:
    def __init__(self):
        self.config = configurable.Configuration(["archiveofourown.org"], "html")
        
        # TODO: Migrate into a fetcher.ini.
        personal_settings = """
[defaults]
is_adult: true
keep_html_attrs: class,id,style
user_agent: pyao3-reader
slow_down_sleep_time: 2
use_view_full_work: true
        """
        self.config.read_string(personal_settings)

    async def fetch_formatted_chapters(self, url: str) -> list[ChapterData]:
        return await asyncio.to_thread(self._sync_fetch, url)

    def _sync_fetch(self, url: str) -> list[ChapterData]:
        adapter = adapters.getAdapter(self.config, url)
        
        # 1. This triggers the OTW/AO3 specific scraping logic
        adapter.extractChapterUrlsAndMetadata()
        
        # 2. Get the list of chapter objects using the getter method
        # These objects typically have 'title' and 'url' attributes
        fetched_chapters = adapter.get_chapters()
        
        chapters_data = []
        
        # 3. Iterate through the chapters
        for i, chapter in enumerate(fetched_chapters):
            # BaseOTWAdapter's getChapterTextNum requires the URL and the 0-based index
            # Note: chapter['url'] works if it's a dict, or chapter.url if it's an object. 
            # FFF usually returns objects with a __getitem__ fallback.
            chapter_url = chapter['url']
            chapter_title = chapter['title']
            
            # This calls the method you see in the BaseOTWAdapter source
            # It handles the view_full_work logic automatically
            chapter_html = adapter.getChapterTextNum(chapter_url, i)
            
            chapters_data.append({
                "index": i + 1,
                "title": chapter_title,
                "html": chapter_html
            })
            
        return chapters_data