import flet as ft
from services.fetcher_service import FetcherService
from models.ao3_types import ChapterData
from typing import List

async def main(page: ft.Page) -> None:
    # 1. Page Configuration
    page.title = "pyao3"
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.padding = 0
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.fonts = {"serif": "https://github.com/google/fonts/raw/main/ofl/merriweather/Merriweather-Regular.ttf"}

    # 2. State Management
    chapters: List[ChapterData] = []
    fetcher = FetcherService()

    # 3. UI Component References
    loading_ring = ft.Container(
        content=ft.ProgressRing(width=40, height=40, stroke_width=4),
        alignment=ft.alignment.Alignment.CENTER,
        visible=False,
        expand=True
    )

    reader_title = ft.Text("", size=28, weight=ft.FontWeight.BOLD, font_family="serif")
    reader_divider = ft.Divider(height=30)
    reader_markdown = ft.Markdown(
        value="",
        selectable=True,
        extension_set=ft.MarkdownExtensionSet.GITHUB_FLAVORED,
        expand=True,
        md_style_sheet=ft.MarkdownStyleSheet(
            p_text_style=ft.TextStyle(size=18, height=1.6, font_family="serif"),
            blockquote_text_style=ft.TextStyle(italic=True, color=ft.Colors.GREY_400),
            blockquote_decoration=ft.BoxDecoration(border=ft.border.only(left=ft.BorderSide(4, ft.Colors.BLUE_GREY_700))),
        )
    )

    # Combined layout
    reader_column = ft.Column(
        [loading_ring, reader_title, reader_divider, reader_markdown], 
        scroll=ft.ScrollMode.ALWAYS, 
        expand=True
    )
    reader_container = ft.Container(content=reader_column, padding=ft.padding.only(left=20, right=20, top=30, bottom=40), width=800, expand=True)

    # 4. Async UI Handlers
    async def update_chapter_view(index: int) -> None:
        """Lazy-loads chapter content with a visual loading ring."""
        chapter = chapters[index]
        
        # If content isn't cached, show the ring and hide the text components
        if not chapter["markdown"]:
            loading_ring.visible = True
            reader_title.visible = False
            reader_divider.visible = False
            reader_markdown.visible = False
            page.update()
            
            try:
                md_content = await fetcher.fetch_single_chapter(index)
                chapters[index]["markdown"] = md_content
            except Exception as e:
                loading_ring.visible = False
                reader_markdown.visible = True
                reader_markdown.value = f"**Error loading chapter:** {e}"
                page.update()
                return

        # Hide ring and show content
        loading_ring.visible = False
        reader_title.visible = True
        reader_divider.visible = True
        reader_markdown.visible = True
        
        reader_title.value = chapters[index]["title"]
        reader_markdown.value = chapters[index]["markdown"]
        
        page.update()
        # Scroll to top after content is rendered
        await reader_column.scroll_to(offset=0, duration=300)

    async def on_chapter_select(e: ft.ControlEvent) -> None:
        index = int(e.control.selected_index)
        await page.close_drawer() 
        await update_chapter_view(index)

    async def toggle_drawer(e: ft.ControlEvent) -> None:
        await page.show_drawer()

    # 5. Background Task
    async def load_content_task():
        nonlocal chapters
        try:
            # TODO: Make dynamic.
            work_url = "https://archiveofourown.org/works/71840866"
            chapters = await fetcher.fetch_metadata(work_url)

            drawer_items = [
                ft.NavigationDrawerDestination(
                    label=c['title'],
                    icon=ft.icons.Icons.BOOK_OUTLINED,
                    selected_icon=ft.icons.Icons.BOOK,
                ) for c in chapters
            ]

            page.drawer = ft.NavigationDrawer(
                controls=[ft.Container(height=12), ft.Text("   Chapters", size=20, weight=ft.FontWeight.BOLD), ft.Divider(), *drawer_items],
                on_change=on_chapter_select
            )

            page.appbar = ft.AppBar(
                leading=ft.IconButton(ft.icons.Icons.MENU, on_click=toggle_drawer),
                title=ft.Text("pyao3"),
                bgcolor=ft.Colors.SURFACE,
            )

            page.controls.clear()
            page.vertical_alignment = ft.MainAxisAlignment.START
            page.horizontal_alignment = ft.CrossAxisAlignment.START
            page.add(ft.Row([reader_container], alignment=ft.MainAxisAlignment.CENTER, expand=True))
            
            await update_chapter_view(0)
            
        except Exception as e:
            page.controls.clear()
            page.add(ft.Text(f"Error: {e}", color=ft.Colors.RED))
            page.update()

    # 6. Initial Loading UI (First app launch)
    page.add(ft.Column([ft.ProgressRing(width=40), ft.Text("Loading metadata...", italic=True)], horizontal_alignment=ft.CrossAxisAlignment.CENTER))

    # 7. Start the Background Task
    page.run_task(load_content_task)

if __name__ == "__main__":
    ft.run(main)