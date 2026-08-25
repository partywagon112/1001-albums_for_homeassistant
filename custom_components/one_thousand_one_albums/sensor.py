"""Sensors for 1001 Albums."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import aiohttp

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_PROJECT, DEFAULT_PROJECT, DOMAIN, build_project_url


class AlbumCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch the current album."""

    def __init__(self, hass, session: aiohttp.ClientSession, project: str) -> None:
        super().__init__(
            hass,
            name=DOMAIN,
            update_interval=timedelta(hours=1),
        )
        self.session = session
        self.url = build_project_url(project or DEFAULT_PROJECT)

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            async with self.session.get(self.url, timeout=20) as response:
                response.raise_for_status()
                text = await response.text()

            import json
            payload = json.loads(text)
            return payload.get("currentAlbum", payload)

        except Exception as err:
            raise UpdateFailed(f"Error fetching album: {err}") from err


class AlbumValueSensor(SensorEntity):
    """Generic sensor for a single field in the current album payload."""

    def __init__(
        self,
        coordinator: AlbumCoordinator,
        field: str,
        name: str | None = None,
        unique_id: str | None = None,
    ) -> None:
        self.coordinator = coordinator
        self.field = field
        self._attr_name = name or field
        self._attr_unique_id = unique_id or f"{DOMAIN}_{field}"

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

    @property
    def state(self) -> str:
        data = self.coordinator.data or {}
        value = data.get(self.field, "")
        if value is None:
            return "unknown"
        if isinstance(value, (dict, list)):
            return str(value)
        return str(value)


class AlbumNameSensor(AlbumValueSensor):
    """Current album name."""

    def __init__(self, coordinator: AlbumCoordinator, name: str, unique_id: str) -> None:
        super().__init__(coordinator, "name", name, unique_id)


class AlbumArtistSensor(AlbumValueSensor):
    """Current album artist."""

    def __init__(self, coordinator: AlbumCoordinator, name: str, unique_id: str) -> None:
        super().__init__(coordinator, "artist", name, unique_id)


class AlbumArtSensor(AlbumValueSensor):
    """Current album cover."""

    def __init__(self, coordinator: AlbumCoordinator, name: str, unique_id: str) -> None:
        super().__init__(coordinator, "image", name, unique_id)

    @property
    def state(self) -> str:
        data = self.coordinator.data or {}
        images = data.get("images", [])
        if not images:
            return "unknown"
        return str(images[0].get("url", "unknown"))

    @property
    def entity_picture(self) -> str | None:
        data = self.coordinator.data or {}
        images = data.get("images", [])
        if not images:
            return None
        return str(images[0].get("url"))


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up sensors from a config entry."""

    session = aiohttp.ClientSession()

    project = (
        config_entry.options.get(CONF_PROJECT)
        or config_entry.data.get(CONF_PROJECT)
        or DEFAULT_PROJECT
    )

    coordinator = AlbumCoordinator(hass, session, project)
    await coordinator.async_config_entry_first_refresh()

    fields = [
        "name",
        "artist",
        "artistOrigin",
        "releaseDate",
        "globalReviewsUrl",
        "wikipediaUrl",
        "spotifyId",
        "appleMusicId",
        "tidalId",
        "amazonMusicId",
        "youtubeMusicId",
        "qobuzId",
        "deezerId",
        "slug",
        "uuid",
        "shareableUrl",
        "currentAlbumNotes",
        "updateFrequency",
    ]

    entities = [
        AlbumValueSensor(coordinator, field, field.replace("currentAlbum", "Current album").replace("artistOrigin", "Artist origin").replace("globalReviewsUrl", "Global reviews URL").replace("wikipediaUrl", "Wikipedia URL").replace("spotifyId", "Spotify ID").replace("appleMusicId", "Apple Music ID").replace("tidalId", "Tidal ID").replace("amazonMusicId", "Amazon Music ID").replace("youtubeMusicId", "YouTube Music ID").replace("qobuzId", "Qobuz ID").replace("deezerId", "Deezer ID").replace("releaseDate", "Release date").replace("shareableUrl", "Shareable URL").replace("currentAlbumNotes", "Current album notes").replace("updateFrequency", "Update frequency").replace("uuid", "UUID").replace("slug", "Slug"), f"{DOMAIN}_{field}")
        for field in fields
    ]
    entities.append(AlbumArtSensor(coordinator, "image", "Album cover art", f"{DOMAIN}_album_art"))
    async_add_entities(entities, True)
