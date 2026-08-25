"""Sensors for 1001 Albums."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import aiohttp

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import CONF_PROJECT, DEFAULT_PROJECT, DOMAIN, build_project_url


class AlbumCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch the current 1001 Albums project data."""

    def __init__(
        self,
        hass,
        session: aiohttp.ClientSession,
        project: str,
    ) -> None:
        super().__init__(
            hass,
            name=DOMAIN,
            update_interval=timedelta(hours=1),
        )

        self.session = session
        self.url = build_project_url(project or DEFAULT_PROJECT)

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch project JSON."""
        try:
            async with self.session.get(
                self.url,
                timeout=20,
            ) as response:
                response.raise_for_status()
                return await response.json()

        except Exception as err:
            raise UpdateFailed(
                f"Error fetching 1001 Albums: {err}"
            ) from err


class AlbumValueSensor(SensorEntity):
    """Sensor for a value from the project or current album."""

    def __init__(
        self,
        coordinator: AlbumCoordinator,
        field: str,
        name: str,
        unique_id: str,
        source: str = "album",
    ) -> None:
        self.coordinator = coordinator
        self.field = field
        self.source = source

        self._attr_name = name
        self._attr_unique_id = unique_id

    @property
    def available(self) -> bool:
        """Return whether data is available."""
        return self.coordinator.last_update_success

    @property
    def state(self) -> str:
        """Return the sensor state."""
        data = self.coordinator.data or {}

        if self.source == "album":
            data = data.get("currentAlbum", {})

        value = data.get(self.field)

        if value is None:
            return "unknown"

        return str(value)


class AlbumArtSensor(AlbumValueSensor):
    """Sensor for the current album cover."""

    def __init__(
        self,
        coordinator: AlbumCoordinator,
        name: str,
        unique_id: str,
    ) -> None:
        super().__init__(
            coordinator,
            "images",
            name,
            unique_id,
        )

    @property
    def state(self) -> str:
        """Return the album name."""
        album = self.coordinator.data.get("currentAlbum", {})

        return str(album.get("name", "unknown"))

    @property
    def entity_picture(self) -> str | None:
        """Return the album cover URL."""
        album = self.coordinator.data.get("currentAlbum", {})
        images = album.get("images", [])

        if not images:
            return None

        return images[0].get("url")


async def async_setup_entry(
    hass,
    config_entry,
    async_add_entities,
) -> None:
    """Set up sensors from a config entry."""

    session = aiohttp.ClientSession()

    project = (
        config_entry.options.get(CONF_PROJECT)
        or config_entry.data.get(CONF_PROJECT)
        or DEFAULT_PROJECT
    )

    coordinator = AlbumCoordinator(
        hass,
        session,
        project,
    )

    await coordinator.async_config_entry_first_refresh()

    entities = [
        # Current album
        AlbumValueSensor(
            coordinator,
            "name",
            "Album",
            f"{DOMAIN}_album_name",
        ),
        AlbumValueSensor(
            coordinator,
            "artist",
            "Artist",
            f"{DOMAIN}_artist",
        ),
        AlbumValueSensor(
            coordinator,
            "artistOrigin",
            "Artist origin",
            f"{DOMAIN}_artist_origin",
        ),
        AlbumValueSensor(
            coordinator,
            "releaseDate",
            "Release date",
            f"{DOMAIN}_release_date",
        ),
        AlbumValueSensor(
            coordinator,
            "slug",
            "Slug",
            f"{DOMAIN}_slug",
        ),
        AlbumValueSensor(
            coordinator,
            "uuid",
            "UUID",
            f"{DOMAIN}_uuid",
        ),
        AlbumValueSensor(
            coordinator,
            "globalReviewsUrl",
            "Global reviews URL",
            f"{DOMAIN}_global_reviews_url",
        ),
        AlbumValueSensor(
            coordinator,
            "wikipediaUrl",
            "Wikipedia URL",
            f"{DOMAIN}_wikipedia_url",
        ),
        AlbumValueSensor(
            coordinator,
            "spotifyId",
            "Spotify ID",
            f"{DOMAIN}_spotify_id",
        ),
        AlbumValueSensor(
            coordinator,
            "appleMusicId",
            "Apple Music ID",
            f"{DOMAIN}_apple_music_id",
        ),
        AlbumValueSensor(
            coordinator,
            "tidalId",
            "Tidal ID",
            f"{DOMAIN}_tidal_id",
        ),
        AlbumValueSensor(
            coordinator,
            "amazonMusicId",
            "Amazon Music ID",
            f"{DOMAIN}_amazon_music_id",
        ),
        AlbumValueSensor(
            coordinator,
            "youtubeMusicId",
            "YouTube Music ID",
            f"{DOMAIN}_youtube_music_id",
        ),
        AlbumValueSensor(
            coordinator,
            "qobuzId",
            "Qobuz ID",
            f"{DOMAIN}_qobuz_id",
        ),
        AlbumValueSensor(
            coordinator,
            "deezerId",
            "Deezer ID",
            f"{DOMAIN}_deezer_id",
        ),

        # Project-level fields
        AlbumValueSensor(
            coordinator,
            "shareableUrl",
            "Shareable URL",
            f"{DOMAIN}_shareable_url",
            source="project",
        ),
        AlbumValueSensor(
            coordinator,
            "currentAlbumNotes",
            "Album notes",
            f"{DOMAIN}_album_notes",
            source="project",
        ),
        AlbumValueSensor(
            coordinator,
            "updateFrequency",
            "Update frequency",
            f"{DOMAIN}_update_frequency",
            source="project",
        ),
        AlbumValueSensor(
            coordinator,
            "name",
            "Project name",
            f"{DOMAIN}_project_name",
            source="project",
        ),

        # Album artwork
        AlbumArtSensor(
            coordinator,
            "Album cover art",
            f"{DOMAIN}_album_art",
        ),
    ]

    async_add_entities(entities, True)
