import flet as ft
from services.fetcher_service import FetcherService
from models.ao3_types import ChapterData
from typing import List

async def main(page: ft.Page) -> None:
    """Application entry point for the PyAo3 Reader."""
    
    # 1. Page Configuration
    page.title = "PyAo3 Reader"
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.scroll = ft.ScrollMode.HIDDEN
    page.padding = 0
    
    # Set alignment to center for the loading screen
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    page.fonts = {
        "serif": "https://github.com/google/fonts/raw/main/ofl/merriweather/Merriweather-Regular.ttf"
    }

    # 2. State Management
    # Defined here so it's accessible to handlers and the background task
    chapters: List[ChapterData] = []

    # 3. UI Component References
    reader_title = ft.Text("", size=28, weight=ft.FontWeight.BOLD, font_family="serif")
    
    reader_markdown = ft.Markdown(
        value="",
        selectable=True,
        extension_set=ft.MarkdownExtensionSet.GITHUB_FLAVORED,
        expand=True,
        md_style_sheet=ft.MarkdownStyleSheet(
            p_text_style=ft.TextStyle(size=18, height=1.6, font_family="serif"),
            h1_text_style=ft.TextStyle(size=24, weight=ft.FontWeight.BOLD),
            blockquote_text_style=ft.TextStyle(italic=True, color=ft.Colors.GREY_400),
            blockquote_padding=ft.padding.only(left=20, top=5, bottom=5),
            blockquote_decoration=ft.BoxDecoration(
                border=ft.border.only(left=ft.BorderSide(4, ft.Colors.BLUE_GREY_700))
            ),
            codeblock_decoration=ft.BoxDecoration(
                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLUE_GREY_100),
                border_radius=ft.border_radius.all(4),
            ),
        )
    )

    reader_column = ft.Column(
        [reader_title, ft.Divider(height=30), reader_markdown],
        scroll=ft.ScrollMode.ALWAYS,
        expand=True,
    )

    reader_container = ft.Container(
        content=reader_column,
        padding=ft.padding.only(left=20, right=20, top=30, bottom=40),
        width=800,
        expand=True
    )

    # 4. Async UI Handlers
    async def update_chapter_view(chapter: ChapterData) -> None:
        """Updates content and resets scroll position."""
        reader_title.value = chapter["title"]
        reader_markdown.value = chapter["markdown"]
        # Animation coroutines MUST be awaited
        await reader_column.scroll_to(offset=0, duration=300)
        page.update() 

    async def on_chapter_select(e: ft.ControlEvent) -> None:
        """Handles selection via the drawer's selected_index."""
        if not chapters:
            return
        # NavigationDrawer.on_change returns the drawer itself as e.control
        index = int(e.control.selected_index)
        await update_chapter_view(chapters[index])
        await page.close_drawer()

    async def toggle_drawer(e: ft.ControlEvent) -> None:
        await page.show_drawer()

    # 5. Background Task
    async def load_content_task():
        nonlocal chapters
        try:
            # A. Fetch Data
            fetcher = FetcherService()
            # TODO: Make dynamic.
            work_url = "https://archiveofourown.org/works/71840866"
            chapters = await fetcher.fetch_formatted_chapters(work_url)

            # B. Build Drawer Items
            drawer_items = [
                ft.NavigationDrawerDestination(
                    label=c['title'],
                    icon=ft.icons.Icons.BOOK_OUTLINED,
                    selected_icon=ft.icons.Icons.BOOK,
                ) for c in chapters
            ]

            # C. Configure App Structure (Drawer & AppBar)
            page.drawer = ft.NavigationDrawer(
                controls=[
                    ft.Container(height=12),
                    ft.Text("   Chapters", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    *drawer_items
                ],
                on_change=on_chapter_select
            )

            page.appbar = ft.AppBar(
                leading=ft.IconButton(ft.icons.Icons.MENU, on_click=toggle_drawer),
                title=ft.Text("PyAo3 Reader"),
                center_title=False,
                bgcolor=ft.Colors.SURFACE,
                actions=[ft.IconButton(ft.icons.Icons.SETTINGS_OUTLINED)]
            )

            # D. Swap UI: Remove Loading -> Add Reader
            page.controls.clear()
            
            # Reset alignment so the reader starts at the top-left
            page.vertical_alignment = ft.MainAxisAlignment.START
            page.horizontal_alignment = ft.CrossAxisAlignment.START
            
            # Add the main reader container centered horizontally
            page.add(
                ft.Row([reader_container], alignment=ft.MainAxisAlignment.CENTER, expand=True)
            )
            
            # E. Initial Data Render
            await update_chapter_view(chapters[0])
            
        except Exception as e:
            page.controls.clear()
            page.add(ft.Text(f"Error: {e}", color=ft.Colors.RED))
            page.update()

    # 6. Initial Loading UI
    loading_view = ft.Column(
        [
            ft.ProgressRing(width=40, stroke_width=3),
            ft.Text("Fetching work...", size=14, italic=True)
        ], 
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
    
    page.add(loading_view)

    # 7. Start the Background Task
    page.run_task(load_content_task)

if __name__ == "__main__":
    ft.run(main)