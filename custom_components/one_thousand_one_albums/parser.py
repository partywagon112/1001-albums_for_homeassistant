"""Helpers for parsing the 1001 Albums project JSON API."""

from __future__ import annotations

import json


def build_auth_headers(api_key: str | None) -> dict[str, str]:
    """The public project API does not require an auth token."""
    return {}


def _best_cover_image(images: list[dict] | None) -> str:
    if not images:
        return ""

    best = None
    for image in images:
        if not isinstance(image, dict):
            continue
        url = image.get("url")
        width = int(image.get("width") or 0)
        height = int(image.get("height") or 0)
        if not url:
            continue
        score = width * height
        if best is None or score > best[0]:
            best = (score, url)

    return best[1] if best else ""


def parse_album_page(payload: str | dict | None) -> dict[str, dict[str, str]]:
    """Parse the current album payload from the public JSON API."""
    today = {"title": "", "artist": "", "image": ""}

    if isinstance(payload, str):
        cleaned = payload.strip()
        if not cleaned:
            return {"today": today}
        try:
            payload = json.loads(cleaned)
        except json.JSONDecodeError:
            title_value = ""
            image_value = ""

            for meta_name in ("og:title", "twitter:title"):
                start = cleaned.find(f'property="{meta_name}"')
                if start == -1:
                    start = cleaned.find(f'name="{meta_name}"')
                if start != -1:
                    content_start = cleaned.find('content="', start)
                    if content_start != -1:
                        content_start += len('content="')
                        content_end = cleaned.find('"', content_start)
                        if content_end != -1:
                            title_value = cleaned[content_start:content_end]
                            break

            for meta_name in ("og:image", "twitter:image"):
                start = cleaned.find(f'property="{meta_name}"')
                if start == -1:
                    start = cleaned.find(f'name="{meta_name}"')
                if start != -1:
                    content_start = cleaned.find('content="', start)
                    if content_start != -1:
                        content_start += len('content="')
                        content_end = cleaned.find('"', content_start)
                        if content_end != -1:
                            image_value = cleaned[content_start:content_end]
                            break

            if title_value:
                if " - " in title_value:
                    title, artist = title_value.split(" - ", 1)
                    title = title.replace("Today:", "", 1).strip()
                    today["title"] = title.strip()
                    today["artist"] = artist.strip()
                else:
                    today["title"] = title_value.strip()
            if image_value:
                today["image"] = image_value.strip()
            return {"today": today}

    if not isinstance(payload, dict):
        return {"today": today}

    album = payload.get("currentAlbum") if isinstance(payload.get("currentAlbum"), dict) else payload
    title = album.get("name") or payload.get("name")
    artist = album.get("artist") or payload.get("artist")
    image = _best_cover_image(album.get("images") or payload.get("images"))

    if title:
        today["title"] = str(title)
    if artist:
        today["artist"] = str(artist)
    if image:
        today["image"] = image

    return {"today": today}
