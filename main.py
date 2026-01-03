import flet as ft
from services.fetcher_service import FetcherService
from services.content_service import ContentService
from models.ao3_types import ChapterData
from typing import List

async def main(page: ft.Page) -> None:
    """Main entry point for the PyAo3 Reader application.

    Handles the application lifecycle: initialization, asynchronous data 
    fetching, and rendering the responsive reader UI.

    Args:
        page: The root Flet Page instance.
    """
    # Setup Page
    page.title = "PyAo3"
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 0  # Padding is handled by internal containers for better control

    # Initialize Services
    fetcher: FetcherService = FetcherService()
    
    # 1. Loading Indicator
    # Using alignment and expand to center the ring in the viewport
    loading = ft.Container(
        content=ft.Column(
            [
                ft.ProgressRing(width=50, height=50, stroke_width=4),
                ft.Text("We're downloading your fic...", italic=True)
            ], 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER
        ),
        expand=True,
        alignment=ft.alignment.Alignment.CENTER
    )
    page.add(loading)

    # 2. Fetch Data
    # TODO: Make this dynamic.
    work_url: str = "https://archiveofourown.org/works/76968931"
    
    chapters: List[ChapterData] = await fetcher.fetch_formatted_chapters(work_url)
    
    # Process the first chapter for display
    first_chapter_md: str = ContentService.clean_html_for_flet(chapters[0]["html"])

    # 3. Build the Reader UI
    # Used ft.Padding.only (Class-based) to resolve DeprecationWarning
    # Added expand=True to ensure the container flexes with the window size
    reader_content: ft.Container = ft.Container(
        padding=ft.Padding.only(left=20, right=20, top=40, bottom=40),
        # We use a maximum width for desktop readability but allow it to shrink
        width=800, 
        content=ft.Column(
            [
                ft.Text(
                    chapters[0]["title"], 
                    size=32, 
                    weight=ft.FontWeight.BOLD, 
                    font_family="serif"
                ),
                ft.Divider(height=30),
                ft.Markdown(
                    value=first_chapter_md,
                    selectable=True,
                    extension_set=ft.MarkdownExtensionSet.GITHUB_FLAVORED,
                    # Ensure markdown text wraps and fills its container
                    expand=True,
                    md_style_sheet=ft.MarkdownStyleSheet(
                        p_text_style=ft.TextStyle(
                            size=18, 
                            height=1.6, 
                            font_family="serif"
                        )
                    )
                ),
            ],
            expand=True,
        ),
    )

    # 4. Final Render
    # page.clean() removes the loading indicator
    page.clean()
    
    # Wrapping in an expanded Row/Column combination ensures 
    # the 800px container remains centered and responsive.
    page.add(
        ft.Row(
            [
                ft.Column(
                    [reader_content],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )
    page.update()

if __name__ == "__main__":
    ft.run(main)