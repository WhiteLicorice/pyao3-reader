from markdownify import markdownify as md

class ContentService:
    """Service for processing and cleaning content for UI display."""

    @staticmethod
    def clean_html_for_flet(html_content: str) -> str:
        """Converts raw AO3 HTML to readable Markdown for Flet components.

        Args:
            html_content: The raw HTML string extracted from the AO3 adapter.

        Returns:
            A cleaned Markdown string compatible with ft.Markdown.
        """
        markdown_text: str = md(
            html_content,
            heading_style="ATX",
            bullets="-",
            strip=['script', 'style']
        )
        return markdown_text.strip()