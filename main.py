from __future__ import annotations

from AO3 import Work
from utils.common import get_authors, resolve_to_work

import flet as ft

def main(page: ft.Page):
    curr_work: Work = resolve_to_work(38114002)
    curr_chapter: int = 0
    line_height = 2.0

    page.title = f"{curr_work.title} by {str(get_authors(curr_work))}"
    page.vertical_alignment = "center"

    page.add(
        ft.Container(
            content=ft.ListView(
                controls=[
                    ft.Text(
                        value=curr_work.chapters[curr_chapter].text,
                        theme_style=ft.TextThemeStyle.BODY_LARGE,
                        style=ft.TextStyle(height=line_height),
                    )
                ],
            ),
            expand=True,
        )
    )

ft.app(target=main)