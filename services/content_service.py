from markdownify import markdownify as md

class ContentService:
    @staticmethod
    def clean_html_for_flet(html_content: str) -> str:
        """Converts raw AO3 HTML to readable Markdown."""
        # Convert to Markdown while preserving structural elements
        markdown_text = md(
            html_content,
            heading_style="ATX",
            bullets="-",
            strip=['script', 'style']
        )
        return markdown_text.strip()