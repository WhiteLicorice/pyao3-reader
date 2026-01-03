import flet as ft
from services.fetcher_service import FetcherService
from models.ao3_types import ChapterData
from typing import List

async def main(page: ft.Page) -> None:
    """Application entry point."""
    page.title = "PyAo3"
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.scroll = ft.ScrollMode.HIDDEN # Use the container for scrolling
    page.padding = 0

    fetcher: FetcherService = FetcherService()
    
    # UI Component: Loading State
    loading_view = ft.Container(
        content=ft.Column([
            ft.ProgressRing(width=50, height=50),
            ft.Text("Downloading your fic...", italic=True)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        expand=True,
        alignment=ft.alignment.Alignment.CENTER
    )

    page.add(loading_view)

    try:
        # 1. Background Fetch
        work_url: str = "https://archiveofourown.org/works/76968931"
        chapters: List[ChapterData] = await fetcher.fetch_formatted_chapters(work_url)
        
        # 2. Prepare Reader Component
        # Using a Column with scroll=ALWAYS inside the reader_content
        reader_column = ft.Column(
            [
                ft.Text(chapters[0]["title"], size=32, weight=ft.FontWeight.BOLD, font_family="serif"),
                ft.Divider(height=30),
                ft.Markdown(
                    value=chapters[0]["markdown"],
                    selectable=True,
                    extension_set=ft.MarkdownExtensionSet.GITHUB_FLAVORED,
                    expand=True,
                    md_style_sheet=ft.MarkdownStyleSheet(
                        p_text_style=ft.TextStyle(size=18, height=1.6, font_family="serif")
                    )
                ),
            ],
            scroll=ft.ScrollMode.ALWAYS,
            expand=True,
        )

        reader_container = ft.Container(
            content=reader_column,
            padding=ft.Padding.only(left=20, right=20, top=40, bottom=40),
            width=800,
            expand=True
        )

        # 3. Controlled Swap
        page.controls.remove(loading_view)
        page.add(
            ft.Row(
                [reader_container],
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True
            )
        )
        
    except Exception as e:
        page.clean()
        page.add(ft.Text(f"Failed to load fic: {e}", color=ft.colors.RED_700))
    
    page.update()

if __name__ == "__main__":
    # ft.app has been deprecated, use ft.run instead
    ft.run(main)