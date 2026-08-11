from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Tag

from radar_ufersa.models import PageAnchor

_CONTEXT_ANCHOR_TITLES = frozenset({"consultar", "arquivo", "pdf", "clique aqui"})


class BeautifulSoupAnchorExtractor:
    def extract(self, base_url: str, html: str) -> tuple[PageAnchor, ...]:
        """Extracts content links while ignoring navigation-only URL schemes.

        Example: ``extractor.extract(page_url, '<main><a href="/x">X</a></main>')``.
        """
        soup = BeautifulSoup(html, "html.parser")
        root = self._find_content_root(soup)
        anchors = tuple(
            self._convert_anchor(base_url, tag) for tag in root.find_all("a")
        )
        valid_anchors = tuple(anchor for anchor in anchors if anchor is not None)
        return tuple(dict.fromkeys(valid_anchors))

    def _find_content_root(self, soup: BeautifulSoup) -> Tag | BeautifulSoup:
        main = soup.find("main")
        if isinstance(main, Tag):
            return main
        entry_content = soup.find(class_="entry-content")
        if isinstance(entry_content, Tag):
            return entry_content
        return soup.body if isinstance(soup.body, Tag) else soup

    def _convert_anchor(self, base_url: str, tag: Tag) -> PageAnchor | None:
        href_value = tag.get("href")
        if not isinstance(href_value, str) or not self._is_supported_href(href_value):
            return None
        title = self._build_title(tag)
        if not title:
            return None
        return PageAnchor(title=title, url=urljoin(base_url, href_value))

    def _build_title(self, tag: Tag) -> str:
        anchor_title = " ".join(tag.get_text(" ", strip=True).split())
        if not self._needs_context(anchor_title):
            return anchor_title
        context_title = self._find_context_title(tag)
        return context_title or anchor_title

    def _needs_context(self, anchor_title: str) -> bool:
        normalized_title = anchor_title.casefold().strip()
        if normalized_title in _CONTEXT_ANCHOR_TITLES:
            return True
        return normalized_title.startswith("portaria nº")

    def _find_context_title(self, tag: Tag) -> str:
        parent = tag.find_parent(("tr", "li", "p"))
        if not isinstance(parent, Tag):
            return ""
        context_title = " ".join(parent.get_text(" ", strip=True).split())
        return context_title if len(context_title) <= 400 else ""

    def _is_supported_href(self, href_value: str) -> bool:
        stripped_href = href_value.strip()
        if not stripped_href or stripped_href.startswith("#"):
            return False
        scheme = urlparse(stripped_href).scheme.lower()
        return scheme in ("", "http", "https")
