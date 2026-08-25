"""The 1001 Albums custom integration."""

from __future__ import annotations

from typing import Any

try:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.typing import ConfigType
except ImportError:  # pragma: no cover - only used outside Home Assistant
    HomeAssistant = Any
    ConfigType = dict

DOMAIN = "one_thousand_one_albums"


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the integration from YAML."""
    return True
