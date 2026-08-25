"""The 1001 Albums custom integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from datetime import timedelta
import aiohttp
import logging

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_PROJECT, DEFAULT_PROJECT, DOMAIN, build_project_url

_LOGGER = logging.getLogger(__name__)
DEFAULT_SCAN_INTERVAL = timedelta(minutes=30)

from .const import DOMAIN

PLATFORMS = ["sensor", "camera"]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the 1001 Albums integration."""
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Set up 1001 Albums from a config entry."""
    project = entry.data.get(CONF_PROJECT, DEFAULT_PROJECT)
    url = build_project_url(project)

    session = async_get_clientsession(hass)

    async def async_update_data() -> dict:
        try:
            async with session.get(url, timeout=20) as resp:
                if resp.status != 200:
                    raise UpdateFailed(f"Unexpected status {resp.status}")
                return await resp.json()
        except aiohttp.ClientError as err:
            raise UpdateFailed(err) from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{DOMAIN}_{project}",
        update_method=async_update_data,
        update_interval=DEFAULT_SCAN_INTERVAL,
    )

    # store coordinator and session for platform modules
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {"coordinator": coordinator, "session": session}

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    # Schedule platform setup without awaiting importlib.import_module
    # directly in the event loop to avoid detected blocking import calls.
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    )

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Unload 1001 Albums."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
