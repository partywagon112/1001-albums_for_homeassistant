"""Sensors for 1001 Albums."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import aiohttp
import logging

from homeassistant.components.sensor import SensorEntity
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


