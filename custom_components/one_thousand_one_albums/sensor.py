"""Sensors for 1001 Albums."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

try:
    import aiohttp
    from homeassistant.components.sensor import SensorEntity
    from homeassistant.const import ATTR_ATTRIBUTION
    from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
except ImportError:  # pragma: no cover - only used outside Home Assistant
    aiohttp = None

    class SensorEntity:  # type: ignore[no-redef]
        """Fallback stub for tests and static analysis."""

    class DataUpdateCoordinator:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            self.data = None
            self.last_update_success = True

    class UpdateFailed(Exception):
        pass

    ATTR_ATTRIBUTION = "attribution"

from .parser import build_auth_headers, parse_album_page

DOMAIN = "one_thousand_one_albums"
DEFAULT_URL = "https://1001albums.com/"
CONF_URL = "url"


class OneThousandOneAlbumsCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch and cache the album page."""

    def __init__(self, hass, session: aiohttp.ClientSession, url: str) -> None:
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=1),
        )
        self.session = session
        self.url = url or DEFAULT_URL

    async def _async_update_data(self) -> dict[str, Any]:
        headers = build_auth_headers(None)
        try:
            async with self.session.get(self.url, headers=headers, timeout=20) as response:
                response.raise_for_status()
                html = await response.text()
        except Exception as err:  # pragma: no cover - network errors handled by HA
            raise UpdateFailed(f"Error fetching 1001 Albums: {err}") from err

        return parse_album_page(html)


class AlbumSensor(SensorEntity):
    """Base sensor for an album field."""

    _attr_attribution = "Data provided by 1001 Albums"

    def __init__(self, coordinator: DataUpdateCoordinator[dict[str, Any]], field: str, key: str) -> None:
        self.coordinator = coordinator
        self._field = field
        self._key = key
        self._attr_unique_id = f"{DOMAIN}_{field}_{key}"

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

    @property
    def state(self) -> str:
        data = self.coordinator.data or {}
        album = data.get(self._field, {})
        return album.get(self._key, "unknown")

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        data = self.coordinator.data or {}
        album = data.get(self._field, {})
        return {
            ATTR_ATTRIBUTION: self._attr_attribution,
            "title": album.get("title", ""),
            "artist": album.get("artist", ""),
            "image": album.get("image", ""),
        }


class TodayAlbumNameSensor(AlbumSensor):
    def __init__(self, coordinator):
        super().__init__(coordinator, "today", "title")
        self._attr_name = "Today's album"


class TodayAlbumArtistSensor(AlbumSensor):
    def __init__(self, coordinator):
        super().__init__(coordinator, "today", "artist")
        self._attr_name = "Today's artist"


class TodayAlbumArtSensor(AlbumSensor):
    def __init__(self, coordinator):
        super().__init__(coordinator, "today", "image")
        self._attr_name = "Today's cover art"

    @property
    def entity_picture(self) -> str | None:
        return self.coordinator.data.get("today", {}).get("image")


class TomorrowAlbumNameSensor(AlbumSensor):
    def __init__(self, coordinator):
        super().__init__(coordinator, "tomorrow", "title")
        self._attr_name = "Tomorrow's album"


class TomorrowAlbumArtistSensor(AlbumSensor):
    def __init__(self, coordinator):
        super().__init__(coordinator, "tomorrow", "artist")
        self._attr_name = "Tomorrow's artist"


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up sensors from a config entry."""
    session = aiohttp.ClientSession()
    url = config_entry.options.get(CONF_URL) or config_entry.data.get(CONF_URL, DEFAULT_URL)
    coordinator = OneThousandOneAlbumsCoordinator(hass, session, url)
    await coordinator.async_config_entry_first_refresh()

    entities = [
        TodayAlbumNameSensor(coordinator),
        TodayAlbumArtistSensor(coordinator),
        TodayAlbumArtSensor(coordinator),
        TomorrowAlbumNameSensor(coordinator),
        TomorrowAlbumArtistSensor(coordinator),
    ]
    async_add_entities(entities, True)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up sensors from YAML."""
    session = aiohttp.ClientSession()
    url = config.get(CONF_URL, DEFAULT_URL)
    coordinator = OneThousandOneAlbumsCoordinator(hass, session, url)
    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        [
            TodayAlbumNameSensor(coordinator),
            TodayAlbumArtistSensor(coordinator),
            TodayAlbumArtSensor(coordinator),
            TomorrowAlbumNameSensor(coordinator),
            TomorrowAlbumArtistSensor(coordinator),
        ],
        True,
    )


_LOGGER = __import__("logging").getLogger(__name__)
