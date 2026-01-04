import flet as ft
from services.fetcher_service import FetcherService
from models.ao3_types import Ao3Story, Ao3Chapter

async def main(page: ft.Page) -> None:
    """
    Entry point for the pyao3 reader application.
    
    Initializes the page layout, sets up the central reader interface,
    and spawns the background task to fetch the Ao3Story and its metadata.
    """
    page.title = "pyao3"
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.scroll = ft.ScrollMode.HIDDEN
    page.padding = 0
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    page.fonts = {
        "serif": "https://github.com/google/fonts/raw/main/ofl/merriweather/Merriweather-Regular.ttf"
    }

    # App State
    current_story: Ao3Story | None = None
    fetcher: FetcherService = FetcherService()

    loading_ring: ft.Container = ft.Container(
        content=ft.ProgressRing(width=40, height=40, stroke_width=4),
        alignment=ft.alignment.Alignment.CENTER,
        visible=False,
    )

    reader_title: ft.Text = ft.Text(
        "", 
        size=28, 
        weight=ft.FontWeight.BOLD, 
        font_family="serif"
    )
    
    reader_divider: ft.Divider = ft.Divider(height=30)
    
    reader_markdown: ft.Markdown = ft.Markdown(
        value="",
        selectable=False,
        extension_set=ft.MarkdownExtensionSet.GITHUB_FLAVORED,
        expand=True, 
        md_style_sheet=ft.MarkdownStyleSheet(
            p_text_style=ft.TextStyle(size=18, height=1.6, font_family="serif"),
            blockquote_text_style=ft.TextStyle(italic=True, color=ft.Colors.GREY_400),
            blockquote_decoration=ft.BoxDecoration(
                border=ft.border.only(left=ft.BorderSide(4, ft.Colors.BLUE_GREY_700))
            ),
        )
    )

    reader_column: ft.Column = ft.Column(
        controls=[loading_ring, reader_title, reader_divider, reader_markdown],
        scroll=ft.ScrollMode.ALWAYS,
        expand=True,
    )
    
    reader_container: ft.Container = ft.Container(
        content=reader_column,
        width=800,
        expand=True,
        padding=ft.padding.only(left=20, right=20, top=30, bottom=40),
    )

    async def update_chapter_view(index: int) -> None:
        """
        Loads and renders the content for a specific Ao3Chapter.
        
        If the chapter markdown is missing, it triggers an async fetch through 
        the FetcherService and updates the local story state.
        """
        if not current_story:
            return

        chapter: Ao3Chapter = current_story.chapters[index]

        if not chapter.markdown:
            loading_ring.visible = True
            reader_title.visible = False
            reader_divider.visible = False
            reader_markdown.visible = False
            page.update()

            try:
                # fetch_chapter_content mutates the chapter object internally
                await fetcher.fetch_chapter_content(index)
            except Exception as e:
                loading_ring.visible = False
                reader_markdown.visible = True
                reader_markdown.value = f"**Error loading chapter:** {e}"
                page.update()
                return

        loading_ring.visible = False
        reader_title.visible = True
        reader_divider.visible = True
        reader_markdown.visible = True

        reader_title.value = chapter.title
        reader_markdown.value = chapter.markdown

        page.update()
        await reader_column.scroll_to(offset=0, duration=0)

    async def on_chapter_select(e: ft.ControlEvent) -> None:
        """Handles chapter selection from the NavigationDrawer."""
        index: int = int(e.control.selected_index) # magic property, ugh
        await page.close_drawer()
        await update_chapter_view(index)

    async def toggle_drawer(e: ft.ControlEvent) -> None:
        """Opens the NavigationDrawer."""
        await page.show_drawer()

    async def load_content_task() -> None:
        """
        Fetches the complete Ao3Story metadata and initializes the UI components.
        
        Builds the NavigationDrawer from the story's chapter list and sets the 
        AppBar title to match the story metadata.
        """
        nonlocal current_story
        try:
            # TODO: Make dynamic.
            work_url: str = "https://archiveofourown.org/works/71840866"
            current_story = await fetcher.fetch_story(work_url)

            drawer_items: list[ft.NavigationDrawerDestination] = [
                ft.NavigationDrawerDestination(
                    label=chap.title,
                    icon=ft.icons.Icons.BOOK_OUTLINED,
                    selected_icon=ft.icons.Icons.BOOK,
                ) for chap in current_story.chapters
            ]

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
                title=ft.Text(current_story.title),
                bgcolor=ft.Colors.SURFACE,
            )

            page.controls.clear()
            page.vertical_alignment = ft.MainAxisAlignment.START
            page.horizontal_alignment = ft.CrossAxisAlignment.START
            
            # The Row is used as a layout helper to center the 800px 
            # wide reading container on large screens without affecting the 
            # scrollable height of the inner reader_column.
            page.add(
                ft.Row(
                    [reader_container],
                    alignment=ft.MainAxisAlignment.CENTER,
                    expand=True
                )
            )

            await update_chapter_view(0)

        except Exception as e:
            page.controls.clear()
            page.add(ft.Text(f"Error: {e}", color=ft.Colors.RED))
            page.update()

    # Initial bootstrapper UI
    page.add(
        ft.Column(
            [
                ft.ProgressRing(width=40),
                ft.Text("Loading...", italic=True)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

    page.run_task(load_content_task)

if __name__ == "__main__":
    ft.run(main)