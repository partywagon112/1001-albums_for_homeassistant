# 1001 Albums for Home Assistant

A Home Assistant custom integration for 1001 Albums that exposes:

- today’s album title
- today’s artist
- today’s cover art
- tomorrow’s album title
- tomorrow’s artist

This is intended to be installed through HACS as a custom integration repository.

## HACS install

1. Push this repository to GitHub.
2. Open HACS in Home Assistant.
3. Go to the overflow menu and choose Custom repositories.
4. Add the repository URL and select category Integration.
5. Install the 1001 Albums integration.
6. Restart Home Assistant.

Example repository URL:

```text
https://github.com/your-user/1001-albums-hass
```

## YAML configuration

There is no public API key for this site. The integration uses the public album page URL directly.

```yaml
sensor:
  - platform: one_thousand_one_albums
    url: https://1001albums.com/
```

The integration fetches the page and extracts the current album plus tomorrow’s album from the HTML payload.

## Entities

The integration exposes these sensors:

- `sensor.todays_album`
- `sensor.todays_artist`
- `sensor.todays_cover_art`
- `sensor.tomorrows_album`
- `sensor.tomorrows_artist`

The cover-art sensor exposes the image URL through both `entity_picture` and the `image` attribute.

## Repo structure for HACS

```text
.
├── README.md
├── hacs.json
├── custom_components/
│   └── one_thousand_one_albums/
│       ├── __init__.py
│       ├── manifest.json
│       ├── parser.py
│       └── sensor.py
└── tests/
    └── test_parser.py
```

## Notes

- The integration domain is `one_thousand_one_albums`.
- HACS custom repos should be installed from GitHub, not as a zip file.
- There is no API key; this uses the public site URL directly.

## Validation

```bash
python -m unittest tests/test_parser.py -v
```
