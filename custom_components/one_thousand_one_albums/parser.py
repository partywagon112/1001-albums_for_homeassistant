"""Helpers for parsing 1001 Albums page content."""

from __future__ import annotations

import re
from html import unescape


def build_auth_headers(api_key: str | None) -> dict[str, str]:
    """No API key is required; the site is public and URL-based."""
    return {}


def _extract_meta(html: str, name: str) -> str:
    pattern = re.compile(
        rf'<meta[^>]+(?:property|name)=["\']{re.escape(name)}["\'][^>]+content=["\']([^"\']+)["\']',
        re.IGNORECASE,
    )
    match = pattern.search(html)
    if match:
        return unescape(match.group(1)).strip()
    return ""


def _extract_title_artist(value: str) -> tuple[str, str]:
    if not value:
        return "", ""

    cleaned = unescape(value).strip()
    cleaned = re.sub(r"^\s*(today|album of the day)\s*[:\-–—]?\s*", "", cleaned, flags=re.IGNORECASE)

    for separator in (" - ", " — ", " – ", " | "):
        if separator in cleaned:
            left, right = cleaned.split(separator, 1)
            return left.strip(), right.strip()

    if " by " in cleaned.lower():
        left, right = re.split(r"\s+by\s+", cleaned, flags=re.IGNORECASE, maxsplit=1)
        return left.strip(), right.strip()

    return cleaned, ""


def _parse_block(block: str) -> dict[str, str]:
    heading_texts = [
        unescape(re.sub(r'<[^>]+>', '', heading)).strip()
        for heading in re.findall(r'<h[1-3][^>]*>(.*?)</h[1-3]>', block, re.IGNORECASE | re.DOTALL)
    ]
    heading_texts = [
        text for text in heading_texts
        if text and text.lower() not in {"today", "album of the day", "tomorrow", "next album", "album"}
    ]

    artist_matches = re.findall(r'<p[^>]*>(.*?)</p>', block, re.IGNORECASE | re.DOTALL)
    artist_texts = [
        unescape(re.sub(r'<[^>]+>', '', text)).strip()
        for text in artist_matches
    ]
    artist_texts = [
        text for text in artist_texts
        if text and text.lower() not in {"today", "tomorrow", "album", "artist", "next album"}
    ]

    title = heading_texts[0] if heading_texts else ""
    artist = artist_texts[0] if artist_texts else ""

    return {
        "title": title,
        "artist": artist,
    }


def parse_album_page(html: str) -> dict[str, dict[str, str]]:
    """Parse the site HTML into today's and tomorrow's album data.

    This is retained as a fallback while the preferred integration path is a signed
    API request with an API key.
    """
    today = {"title": "", "artist": "", "image": ""}

    title_value = _extract_meta(html, "og:title") or _extract_meta(html, "twitter:title")
    image_value = _extract_meta(html, "og:image") or _extract_meta(html, "twitter:image")
    if title_value:
        today["title"], today["artist"] = _extract_title_artist(title_value)
    if image_value:
        today["image"] = image_value

    tomorrow = {"title": "", "artist": "", "image": ""}

    tomorrow_match = re.search(
        r'(?is)tomorrow.*?<h[1-3][^>]*>(.*?)</h[1-3]>.*?<p[^>]*>(.*?)</p>',
        html,
    )
    if tomorrow_match:
        tomorrow = _parse_block(tomorrow_match.group(0))

    if not today["title"] or not today["artist"]:
        match = re.search(
            r'(?is)<h[1-3][^>]*>.*?(?:today|album of the day).*?</h[1-3]>.*?<h[1-3][^>]*>(.*?)</h[1-3]>.*?<p[^>]*>(.*?)</p>',
            html,
        )
        if match:
            today = _parse_block(match.group(0))

    if not tomorrow["title"] and not tomorrow["artist"]:
        second_match = re.search(
            r'(?is)(?:tomorrow|next album).*?<h[1-3][^>]*>(.*?)</h[1-3]>.*?<p[^>]*>(.*?)</p>',
            html,
        )
        if second_match:
            tomorrow = _parse_block(second_match.group(0))

    return {"today": today, "tomorrow": tomorrow}
