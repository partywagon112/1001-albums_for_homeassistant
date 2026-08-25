"""Sensors for 1001 Albums."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import aiohttp

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_URL, DEFAULT_URL, DOMAIN


class AlbumCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch the current album."""

    def __init__(self, hass, session: aiohttp.ClientSession, url: str) -> None:
        super().__init__(
            hass,
            name=DOMAIN,
            update_interval=timedelta(hours=1),
        )
        self.session = session
        self.url = url or DEFAULT_URL

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            async with self.session.get(self.url, timeout=20) as response:
                response.raise_for_status()
                data = await response.json()

            return data["currentAlbum"]

        except Exception as err:
            raise UpdateFailed(f"Error fetching album: {err}") from err


class AlbumSensor(SensorEntity):
    """Base album sensor."""

    def __init__(
        self,
        coordinator: AlbumCoordinator,
        name: str,
        unique_id: str,
    ) -> None:
        self.coordinator = coordinator
        self._attr_name = name
        self._attr_unique_id = unique_id

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success


class AlbumNameSensor(AlbumSensor):
    """Current album name."""

    @property
    def state(self) -> str:
        return self.coordinator.data.get("name", "Unknown")


class AlbumArtistSensor(AlbumSensor):
    """Current album artist."""

    @property
    def state(self) -> str:
        return self.coordinator.data.get("artist", "Unknown")


class AlbumArtSensor(AlbumSensor):
    """Current album cover."""

    @property
    def state(self) -> str:
        images = self.coordinator.data.get("images", []) if self.coordinator.data else []
        return images[0]["url"] if images else "unknown"

    @property
    def entity_picture(self) -> str | None:
        images = self.coordinator.data.get("images", []) if self.coordinator.data else []
        return images[0]["url"] if images else None


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up sensors from a config entry."""

    session = aiohttp.ClientSession()

    url = (
        config_entry.options.get(CONF_URL)
        or config_entry.data.get(CONF_URL)
        or DEFAULT_URL
    )

    coordinator = AlbumCoordinator(hass, session, url)

    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        [
            AlbumNameSensor(
                coordinator,
                "Today's album",
                f"{DOMAIN}_album_name",
            ),
            AlbumArtistSensor(
                coordinator,
                "Today's artist",
                f"{DOMAIN}_album_artist",
            ),
            AlbumArtSensor(
                coordinator,
                "Today's album cover",
                f"{DOMAIN}_album_art",
            ),
        ]
    )
