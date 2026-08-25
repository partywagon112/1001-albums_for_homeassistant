"""Camera platform for 1001 Albums integration."""

from __future__ import annotations

from typing import Any
import aiohttp
import logging

try:
    from homeassistant.components.camera import CameraEntity
except Exception:  # pragma: no cover - handle HA versions without CameraEntity
    CameraEntity = None

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    """Set up camera platform for the entry using stored coordinator and session."""

    stored = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if not stored:
        _LOGGER.error("Coordinator for entry %s not found in hass.data", entry.entry_id)
        return

    if CameraEntity is None:
        _LOGGER.warning("CameraEntity not available in this Home Assistant; skipping camera platform")
        return

    coordinator = stored["coordinator"]
    session = stored["session"]

    async_add_entities([OneThousandOneAlbumsCamera(coordinator, entry.entry_id, session)], True)


if CameraEntity is not None:
    class OneThousandOneAlbumsCamera(CoordinatorEntity, CameraEntity):
    """Camera entity that returns the 0th image bytes so the UI can display it."""

    def __init__(self, coordinator, entry_id: str, session: aiohttp.ClientSession) -> None:
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
