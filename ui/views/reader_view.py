import flet as ft
from models.ao3_types import Ao3Story
from services.fetcher_service import FetcherService

class ReaderView(ft.View):
    def __init__(self, parent_page: ft.Page, story_id: str):
        super().__init__(route=f"/reader/{story_id}", padding=0)
        self.parent_page = parent_page
        # TODO: Perhaps use ao3-api.
        self.work_url = f"https://archiveofourown.org/works/{story_id}"
        
        # Stateful service unique to THIS story session
        # Stateful, so we can cache the story (don't need to keep querying it while reading)
        self.fetcher = FetcherService()
        
        # UI components
        self.loading_ring = ft.ProgressRing(width=40, visible=False)
        self.reader_title = ft.Text("", size=24, weight="bold", font_family="serif")
        self.reader_markdown = ft.Markdown(
            extension_set=ft.MarkdownExtensionSet.GITHUB_FLAVORED,
            md_style_sheet=ft.MarkdownStyleSheet(
                p_text_style=ft.TextStyle(size=18, height=1.6, font_family="serif")
            )
        )
        
        self.appbar = ft.AppBar(
            leading=ft.IconButton(ft.icons.Icons.ARROW_BACK, on_click=lambda _: self.parent_page.push_route("/")),
            title=ft.Text("Loading..."),
            bgcolor=ft.Colors.SURFACE,
        )

        self.reader_column = ft.Column(
            controls=[self.reader_title, ft.Divider(), self.reader_markdown],
            scroll=ft.ScrollMode.ALWAYS,
            expand=True,
        )

        self.controls = [
            ft.Stack([
                ft.Container(
                    content=self.reader_column,
                    padding=ft.padding.only(left=20, right=20, top=20, bottom=40),
                    alignment=ft.alignment.Alignment.TOP_CENTER,
                ),
                ft.Container(
                    content=self.loading_ring,
                    alignment=ft.alignment.Alignment.CENTER,
                )
            ], expand=True)
        ]

    async def initialize(self):
        """Fetches metadata and builds the Chapter Drawer."""
        self.loading_ring.visible = True
        await self.parent_page.update()

        try:
            # 1. Fetch story metadata
            story = await self.fetcher.fetch_story(self.work_url)
            self.appbar.title = ft.Text(story.title)
            
            # 2. Build the Navigation Drawer (The Chapter List)
            self.drawer = self._build_drawer(story)
            
            # 3. Add a "Menu" button to AppBar now that we have a drawer
            self.appbar.actions = [
                ft.IconButton(ft.icons.Icons.MENU, on_click=lambda _: self.parent_page.show_drawer(self.drawer))
            ]
            
            # 4. Load the first chapter
            await self.update_chapter_view(0)

        except Exception as e:
            self.reader_markdown.value = f"Error: {e}"
        
        self.loading_ring.visible = False
        await self.parent_page.update()

    def _build_drawer(self, story: Ao3Story) -> ft.NavigationDrawer:
        return ft.NavigationDrawer(
            on_change=self.on_chapter_select,
            controls=[
                ft.Container(height=12),
                ft.Text("   Chapters", size=20, weight="bold"),
                ft.Divider(),
                *[ft.NavigationDrawerDestination(
                    label=chap.title,
                    icon=ft.icons.Icons.BOOK_OUTLINED,
                    selected_icon=ft.icons.Icons.BOOK
                ) for chap in story.chapters]
            ]
        )

    async def update_chapter_view(self, index: int) -> None:
        self.loading_ring.visible = True
        await self.parent_page.update()
        
        try:
            # Uses the stateful self.fetcher to get content
            content = await self.fetcher.fetch_chapter_content(index)
            chapter = self.fetcher.story.chapters[index]
            
            self.reader_title.value = chapter.title
            self.reader_markdown.value = content
            await self.reader_column.scroll_to(offset=0, duration=0)
        except Exception as e:
            self.reader_markdown.value = f"Error loading chapter: {e}"
            
        self.loading_ring.visible = False
        await self.parent_page.update()

    async def on_chapter_select(self, e) -> None:
        index = int(e.control.selected_index)
        await self.parent_page.close_drawer()
        await self.update_chapter_view(index)