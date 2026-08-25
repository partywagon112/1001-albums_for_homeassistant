"""Sensors for 1001 Albums."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import aiohttp
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.camera import CameraEntity
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import ATTR_ATTRIBUTION

from .const import CONF_PROJECT, DEFAULT_PROJECT, DOMAIN, build_project_url

_LOGGER = logging.getLogger(__name__)

DEFAULT_SCAN_INTERVAL = timedelta(minutes=30)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    """Set up the 1001 Albums sensors for a config entry."""

    project = entry.data.get(CONF_PROJECT, DEFAULT_PROJECT)
    url = build_project_url(project)

    session = async_get_clientsession(hass)

    async def async_update_data() -> dict[str, Any]:
        try:
            async with session.get(url, timeout=20) as resp:
                if resp.status != 200:
                    raise UpdateFailed(f"Unexpected status {resp.status}")
                return await resp.json()
        except aiohttp.ClientError as err:
            raise UpdateFailed(err) from err

    coordinator = DataUpdateCoordinator[
        dict
    ](
        hass,
        _LOGGER,
        name=f"{DOMAIN}_{project}",
        update_method=async_update_data,
        update_interval=DEFAULT_SCAN_INTERVAL,
    )

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    entities: list[SensorEntity] = [
        OneThousandOneAlbumsNameSensor(coordinator, entry.entry_id),
        OneThousandOneAlbumsReleaseDateSensor(coordinator, entry.entry_id),
        OneThousandOneAlbumsImageSensor(coordinator, entry.entry_id),
        OneThousandOneAlbumsArtistSensor(coordinator, entry.entry_id),
        OneThousandOneAlbumsArtistOriginSensor(coordinator, entry.entry_id),
        OneThousandOneAlbumsListSensor(coordinator, entry.entry_id, "genres", "Genres"),
        OneThousandOneAlbumsListSensor(coordinator, entry.entry_id, "styles", "Styles"),
        OneThousandOneAlbumsListSensor(coordinator, entry.entry_id, "subGenres", "SubGenres"),
        OneThousandOneAlbumsPlayerSensor(coordinator, entry.entry_id, "spotifyId", "Spotify"),
        OneThousandOneAlbumsPlayerSensor(coordinator, entry.entry_id, "appleMusicId", "Apple Music"),
        OneThousandOneAlbumsPlayerSensor(coordinator, entry.entry_id, "tidalId", "Tidal"),
        OneThousandOneAlbumsPlayerSensor(coordinator, entry.entry_id, "amazonMusicId", "Amazon Music"),
        OneThousandOneAlbumsPlayerSensor(coordinator, entry.entry_id, "youtubeMusicId", "YouTube Music"),
        OneThousandOneAlbumsPlayerSensor(coordinator, entry.entry_id, "qobuzId", "Qobuz"),
        OneThousandOneAlbumsPlayerSensor(coordinator, entry.entry_id, "deezerId", "Deezer"),
        OneThousandOneAlbumsNotesSensor(coordinator, entry.entry_id),
        OneThousandOneAlbumsCamera(coordinator, entry.entry_id, session),
    ]

    async_add_entities(entities, True)


class _BaseCoordinatorSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator: DataUpdateCoordinator, entry_id: str) -> None:
        super().__init__(coordinator)
        self._entry_id = entry_id

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        return {ATTR_ATTRIBUTION: "Data provided by 1001albumsgenerator.com"}


class OneThousandOneAlbumsNameSensor(_BaseCoordinatorSensor):
    """Sensor for the current album name."""

    @property
    def name(self) -> str:
        return "1001 Albums - Current Album"

    @property
    def unique_id(self) -> str:
        return f"{self._entry_id}_current_album_name"

    @property
    def state(self) -> Any:
        data = self.coordinator.data or {}
        current = data.get("currentAlbum") or {}
        return current.get("name")


class OneThousandOneAlbumsReleaseDateSensor(_BaseCoordinatorSensor):
    """Sensor for the current album release date."""

    @property
    def name(self) -> str:
        return "1001 Albums - Release Date"

    @property
    def unique_id(self) -> str:
        return f"{self._entry_id}_current_album_release_date"

    @property
    def state(self) -> Any:
        data = self.coordinator.data or {}
        current = data.get("currentAlbum") or {}
        return current.get("releaseDate")


class OneThousandOneAlbumsImageSensor(_BaseCoordinatorSensor):
    """Sensor exposing the 0th image as an entity picture."""

    @property
    def name(self) -> str:
        return "1001 Albums - Cover"

    @property
    def unique_id(self) -> str:
        return f"{self._entry_id}_current_album_cover"

    @property
    def state(self) -> Any:
        # State can be the image URL or a static label
        data = self.coordinator.data or {}
        current = data.get("currentAlbum") or {}
        images = current.get("images") or []
        if images and isinstance(images, list) and images[0].get("url"):
            return images[0].get("url")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        attrs = super().extra_state_attributes or {}
        data = self.coordinator.data or {}
        current = data.get("currentAlbum") or {}
        images = current.get("images") or []
        if images and isinstance(images, list) and images[0].get("url"):
            attrs = dict(attrs)
            attrs["entity_picture"] = images[0].get("url")
        return attrs


class OneThousandOneAlbumsArtistSensor(_BaseCoordinatorSensor):
    """Sensor for the current album artist."""

    @property
    def name(self) -> str:
        return "1001 Albums - Artist"

    @property
    def unique_id(self) -> str:
        return f"{self._entry_id}_current_album_artist"

    @property
    def state(self) -> Any:
        data = self.coordinator.data or {}
        current = data.get("currentAlbum") or {}
        return current.get("artist")


class OneThousandOneAlbumsArtistOriginSensor(_BaseCoordinatorSensor):
    """Sensor for the current album artist origin."""

    @property
    def name(self) -> str:
        return "1001 Albums - Artist Origin"

    @property
    def unique_id(self) -> str:
        return f"{self._entry_id}_current_album_artist_origin"

    @property
    def state(self) -> Any:
        data = self.coordinator.data or {}
        current = data.get("currentAlbum") or {}
        return current.get("artistOrigin")


class OneThousandOneAlbumsListSensor(_BaseCoordinatorSensor):
    """Generic sensor for list fields (genres/styles/subGenres)."""

    def __init__(self, coordinator: DataUpdateCoordinator, entry_id: str, key: str, title: str) -> None:
        super().__init__(coordinator, entry_id)
        self._key = key
        self._title = title

    @property
    def name(self) -> str:
        return f"1001 Albums - {self._title}"

    @property
    def unique_id(self) -> str:
        return f"{self._entry_id}_current_album_{self._key}"

    @property
    def state(self) -> Any:
        data = self.coordinator.data or {}
        current = data.get("currentAlbum") or {}
        values = current.get(self._key) or []
        if isinstance(values, list):
            return ", ".join(str(v) for v in values)
        return values


class OneThousandOneAlbumsPlayerSensor(_BaseCoordinatorSensor):
    """Generic sensor for player IDs like spotifyId, appleMusicId, etc."""

    def __init__(self, coordinator: DataUpdateCoordinator, entry_id: str, key: str, title: str) -> None:
        super().__init__(coordinator, entry_id)
        self._key = key
        self._title = title

    @property
    def name(self) -> str:
        return f"1001 Albums - {self._title}"

    @property
    def unique_id(self) -> str:
        return f"{self._entry_id}_current_album_{self._key}"

    @property
    def state(self) -> Any:
        data = self.coordinator.data or {}
        current = data.get("currentAlbum") or {}
        return current.get(self._key)


class OneThousandOneAlbumsNotesSensor(_BaseCoordinatorSensor):
    """Sensor for currentAlbumNotes."""

    @property
    def name(self) -> str:
        return "1001 Albums - Current Album Notes"

    @property
    def unique_id(self) -> str:
        return f"{self._entry_id}_current_album_notes"

    @property
    def state(self) -> Any:
        data = self.coordinator.data or {}
        current = data.get("currentAlbum") or {}
        return current.get("currentAlbumNotes")


class OneThousandOneAlbumsCamera(CoordinatorEntity, CameraEntity):
    """Camera entity that returns the 0th image bytes so the UI can display it."""

    def __init__(self, coordinator: DataUpdateCoordinator, entry_id: str, session: aiohttp.ClientSession) -> None:
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._session = session

    @property
    def name(self) -> str:
        return "1001 Albums - Cover Camera"

    @property
    def unique_id(self) -> str:
        return f"{self._entry_id}_cover_camera"

    async def async_camera_image(self) -> bytes | None:
        data = self.coordinator.data or {}
        current = data.get("currentAlbum") or {}
        images = current.get("images") or []
        if not (images and isinstance(images, list)):
            return None
        url = images[0].get("url")
        if not url:
            return None
        try:
            async with self._session.get(url, timeout=20) as resp:
                if resp.status != 200:
                    _LOGGER.debug("Image fetch returned %s", resp.status)
                    return None
                return await resp.read()
        except aiohttp.ClientError as err:
            _LOGGER.debug("Error fetching image: %s", err)
            return None



