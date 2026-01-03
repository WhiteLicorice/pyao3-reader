import flet as ft
import AO3
from services.fetcher_service import FetcherService
from services.content_service import ContentService

async def main(page: ft.Page):
    # Setup Page
    page.title = "PyAo3"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 0  # We handle padding in containers

    # Initialize Services
    fetcher = FetcherService()
    
    # 1. Loading Indicator
    loading = ft.Container(
        content=ft.Column([
            ft.ProgressRing(width=50, height=50, stroke_width=4),
            ft.Text("Downloading formatted content...", italic=True)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        expand=True,
        alignment=ft.alignment.Alignment.CENTER
    )
    page.add(loading)

    # 2. Fetch Data (Using a sample work ID)
    work_url = "https://archiveofourown.org/works/76968931"
    chapters = await fetcher.fetch_formatted_chapters(work_url)
    
    # Process the first chapter for display
    first_chapter_md = ContentService.clean_html_for_flet(chapters[0]["html"])

    # 3. Build the Reader UI
    reader_content = ft.Container(
        padding=ft.padding.only(left=20, right=20, top=40, bottom=40),
        width=800, # Desktop readability constraint
        content=ft.Column([
            ft.Text("Chapter 1", size=32, weight="bold", font_family="serif"),
            ft.Divider(height=30),
            ft.Markdown(
                value=first_chapter_md,
                selectable=True,
                extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                md_style_sheet=ft.MarkdownStyleSheet(
                    p_text_style=ft.TextStyle(
                        size=18, 
                        height=1.6, # Line height for readability
                        font_family="serif"
                    )
                )
            )
        ])
    )

    # 4. Final Render
    page.clean()
    page.add(
        ft.Row([reader_content], alignment=ft.MainAxisAlignment.CENTER)
    )
    page.update()

if __name__ == "__main__":
    ft.app(target=main)