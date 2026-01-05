from typing import Optional
import flet as ft
from ui.views.reader_view import ReaderView

async def main(page: ft.Page):
    page.title = "pyao3"
    
    # 1. State/Style Setup
    page.theme_mode = ft.ThemeMode.DARK
    page.fonts = {
        "serif": "https://github.com/google/fonts/raw/main/ofl/merriweather/Merriweather-Regular.ttf"
    }

    # 2. The Router Logic
    async def route_change(e: Optional[str] = None):
        """
        Handles all navigation. 'e' is None when called manually on startup.
        """
        page.views.clear()
        troute = ft.TemplateRoute(page.route)
        
        # --- Route: Library ---
        if troute.match("/"):
            page.views.append(
                ft.View(
                    route="/",
                    controls=[
                        ft.AppBar(title=ft.Text("Library"), bgcolor=ft.Colors.SURFACE),
                        ft.Container(
                            content=ft.ListTile(
                                title=ft.Text("Open Sample Story"),
                                subtitle=ft.Text("Story ID: 71840866"),
                                on_click=await page.push_route("/reader/71840866")
                            ),
                            padding=10
                        ),
                    ],
                )
            )
        
        # --- Route: Reader ---
        elif troute.match("/reader/:id"):
            story_id = troute.id
            reader_view = ReaderView(page, story_id)
            page.views.append(reader_view)
            # Run background fetching without blocking the UI render
            page.run_task(reader_view.initialize)

        #await page.update()

    async def view_pop(e: ft.ViewPopEvent):
        print(len(page.views))
        if len(page.views) > 1:
            page.views.pop()
            top_view = page.views[-1]
            await page.push_route(top_view.route)

    # 3. Wire up handlers
    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    page.add(ft.View(
                    route="/",
                    controls=[
                        ft.AppBar(title=ft.Text("Library"), bgcolor=ft.Colors.SURFACE),
                        ft.Container(
                            content=ft.ListTile(
                                title=ft.Text("Open Sample Story"),
                                subtitle=ft.Text("Story ID: 71840866"),
                                on_click=await page.push_route("/reader/71840866")
                            ),
                            padding=10
                        ),
                    ],
                ))
    
if __name__ == "__main__":
    ft.app(target=main)