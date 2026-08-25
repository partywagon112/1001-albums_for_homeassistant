import unittest

try:
    from custom_components.one_thousand_one_albums.parser import build_auth_headers, parse_album_page
    from custom_components.one_thousand_one_albums.sensor import AlbumArtSensor, AlbumArtistSensor, AlbumNameSensor
except ModuleNotFoundError:
    import sys
    import types

    # Provide lightweight stubs so the unit tests still execute in a plain Python environment.
    homeassistant = types.ModuleType("homeassistant")
    components = types.ModuleType("homeassistant.components")
    sensor_mod = types.ModuleType("homeassistant.components.sensor")
    helpers = types.ModuleType("homeassistant.helpers")
    coordinator_mod = types.ModuleType("homeassistant.helpers.update_coordinator")

    class SensorEntity:
        pass

    class DataUpdateCoordinator:
        def __init__(self, *args, **kwargs):
            self.data = None
            self.last_update_success = True

        def __class_getitem__(cls, item):
            return cls

    class UpdateFailed(Exception):
        pass

    sensor_mod.SensorEntity = SensorEntity
    coordinator_mod.DataUpdateCoordinator = DataUpdateCoordinator
    coordinator_mod.UpdateFailed = UpdateFailed

    homeassistant.components = components
    components.sensor = sensor_mod
    homeassistant.helpers = helpers
    helpers.update_coordinator = coordinator_mod

    sys.modules["homeassistant"] = homeassistant
    sys.modules["homeassistant.components"] = components
    sys.modules["homeassistant.components.sensor"] = sensor_mod
    sys.modules["homeassistant.helpers"] = helpers
    sys.modules["homeassistant.helpers.update_coordinator"] = coordinator_mod

    # stub aiohttp
    aiohttp = types.ModuleType("aiohttp")
    class ClientSession:
        pass
    aiohttp.ClientSession = ClientSession
    sys.modules["aiohttp"] = aiohttp

    import importlib.util
    from pathlib import Path

    pkg = types.ModuleType("custom_components")
    subpkg = types.ModuleType("custom_components.one_thousand_one_albums")
    for name in ["custom_components", "custom_components.one_thousand_one_albums"]:
        sys.modules[name] = pkg if name == "custom_components" else subpkg

    for module_name, file_name in [
        ("custom_components.one_thousand_one_albums.const", "custom_components/one_thousand_one_albums/const.py"),
        ("custom_components.one_thousand_one_albums.sensor", "custom_components/one_thousand_one_albums/sensor.py"),
        ("custom_components.one_thousand_one_albums.parser", "custom_components/one_thousand_one_albums/parser.py"),
    ]:
        spec = importlib.util.spec_from_file_location(module_name, Path(file_name))
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

    build_auth_headers = sys.modules["custom_components.one_thousand_one_albums.parser"].build_auth_headers
    parse_album_page = sys.modules["custom_components.one_thousand_one_albums.parser"].parse_album_page
    AlbumNameSensor = sys.modules["custom_components.one_thousand_one_albums.sensor"].AlbumNameSensor
    AlbumArtistSensor = sys.modules["custom_components.one_thousand_one_albums.sensor"].AlbumArtistSensor
    AlbumArtSensor = sys.modules["custom_components.one_thousand_one_albums.sensor"].AlbumArtSensor


HTML = '''
<html>
  <head>
    <meta property="og:title" content="Today: The Dark Side of the Moon - Pink Floyd" />
    <meta property="og:image" content="https://example.com/cover.jpg" />
    <meta name="description" content="Artist: Pink Floyd | Album: The Dark Side of the Moon" />
  </head>
  <body>
    <h1>Album of the Day</h1>
    <div class="album-card">
      <h2>The Dark Side of the Moon</h2>
      <p>Pink Floyd</p>
    </div>
  </body>
</html>
'''

JSON_PAYLOAD = {
    "name": "Hard Again",
    "artist": "Muddy Waters",
    "images": [
        {"url": "https://example.com/cover-small.jpg", "width": 64, "height": 64},
        {"url": "https://example.com/cover-large.jpg", "width": 640, "height": 640},
    ],
}


class ParseAlbumPageTests(unittest.TestCase):
    def test_parses_today_album_from_html(self):
        data = parse_album_page(HTML)

        self.assertEqual(data["today"]["title"], "The Dark Side of the Moon")
        self.assertEqual(data["today"]["artist"], "Pink Floyd")
        self.assertEqual(data["today"]["image"], "https://example.com/cover.jpg")

    def test_parses_current_album_from_project_json(self):
        data = parse_album_page(JSON_PAYLOAD)

        self.assertEqual(data["today"]["title"], "Hard Again")
        self.assertEqual(data["today"]["artist"], "Muddy Waters")
        self.assertEqual(data["today"]["image"], "https://example.com/cover-large.jpg")

    def test_no_auth_key_is_required(self):
        headers = build_auth_headers("abc123")

        self.assertEqual(headers, {})

    def test_current_album_sensor_fields(self):
        class FakeCoordinator:
            data = {
                "name": "Hard Again",
                "artist": "Muddy Waters",
                "images": [{"url": "https://example.com/cover-large.jpg"}],
            }
            last_update_success = True

        coordinator = FakeCoordinator()

        name_sensor = AlbumNameSensor(coordinator, "Today's album", "album_name")
        artist_sensor = AlbumArtistSensor(coordinator, "Today's artist", "album_artist")
        art_sensor = AlbumArtSensor(coordinator, "Today's album cover", "album_art")

        self.assertEqual(name_sensor.state, "Hard Again")
        self.assertEqual(artist_sensor.state, "Muddy Waters")
        self.assertEqual(art_sensor.state, "https://example.com/cover-large.jpg")
        self.assertEqual(art_sensor.entity_picture, "https://example.com/cover-large.jpg")

if __name__ == "__main__":
    unittest.main()
