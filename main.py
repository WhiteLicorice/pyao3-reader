import flet as ft
from services.fetcher_service import FetcherService
from models.ao3_types import ChapterData

async def main(page: ft.Page) -> None:
    """
    Entry point for the pyao3 reader application.
    
    Initializes the page layout, sets up the central reader interface,
    and spawns the background task to fetch novel metadata.
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

    chapters: list[ChapterData] = []
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
        Loads and renders the content for a specific chapter index.
        
        Checks if the chapter content is cached in memory. If not, fetches it
        asynchronously, caches it, and then updates the UI.
        """
        chapter: ChapterData = chapters[index]

        if not chapter["markdown"]:
            # Transition to loading state
            loading_ring.visible = True
            reader_title.visible = False
            reader_divider.visible = False
            reader_markdown.visible = False
            page.update()

            try:
                md_content: str = await fetcher.fetch_single_chapter(index)
                chapters[index]["markdown"] = md_content
            except Exception as e:
                loading_ring.visible = False
                reader_markdown.visible = True
                reader_markdown.value = f"**Error loading chapter:** {e}"
                page.update()
                return

        # Render content
        loading_ring.visible = False
        reader_title.visible = True
        reader_divider.visible = True
        reader_markdown.visible = True

        reader_title.value = chapters[index]["title"]
        reader_markdown.value = chapters[index]["markdown"]

        page.update()
        
        # Reset scroll position to top when changing chapters
        await reader_column.scroll_to(offset=0, duration=300)

    async def on_chapter_select(e: ft.ControlEvent) -> None:
        """Callback for the NavigationDrawer to switch chapters."""
        index: int = int(e.control.selected_index)
        await page.close_drawer()
        await update_chapter_view(index)

    async def toggle_drawer(e: ft.ControlEvent) -> None:
        """Callback for the AppBar menu button to open the drawer."""
        await page.show_drawer()

    async def load_content_task() -> None:
        """
        Background initialization task.
        
        Fetches the Work metadata, builds the NavigationDrawer, and sets up 
        the main reading layout once data is ready.
        """
        nonlocal chapters
        try:
            # TODO: Make dynamic.
            work_url: str = "https://archiveofourown.org/works/71840866"
            chapters = await fetcher.fetch_metadata(work_url)

            drawer_items: list[ft.NavigationDrawerDestination] = [
                ft.NavigationDrawerDestination(
                    label=c['title'],
                    icon=ft.icons.Icons.BOOK_OUTLINED,
                    selected_icon=ft.icons.Icons.BOOK,
                ) for c in chapters
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
                title=ft.Text("pyao3"),
                bgcolor=ft.Colors.SURFACE,
            )

            # Clear loading screen and build main UI
            page.controls.clear()
            page.vertical_alignment = ft.MainAxisAlignment.START
            page.horizontal_alignment = ft.CrossAxisAlignment.START
            
            # We wrap the container in a Row with alignment=CENTER
            # to horizontally center the reading view on wide screens (desktop/tablet)
            # while maintaining the vertical scroll behavior of the inner Column.
            page.add(
                ft.Row(
                    [reader_container],
                    alignment=ft.MainAxisAlignment.CENTER,
                    expand=True
                )
            )

            # Load the first chapter by default
            await update_chapter_view(0)

        except Exception as e:
            page.controls.clear()
            page.add(ft.Text(f"Error: {e}", color=ft.Colors.RED))
            page.update()

    # Initial Loading State
    page.add(
        ft.Column(
            [
                ft.ProgressRing(width=40),
                ft.Text("Loading metadata...", italic=True)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )
    page.run_task(load_content_task)

if __name__ == "__main__":
    ft.run(main)