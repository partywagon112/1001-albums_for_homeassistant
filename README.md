# 1001 Albums for Home Assistant

A Home Assistant custom integration for 1001 Albums that exposes:

- today’s album title
- today’s artist
- today’s cover art

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
https://github.com/partywagon112/1001-albums-hass
```

## YAML configuration

This integration uses the public project API: 

```yaml
sensor:
  - platform: one_thousand_one_albums
    url: https://1001albumsgenerator.com/api/v1/projects/patrick-curtain
```

The integration fetches the current album payload from the project endpoint and exposes the live album metadata.

## Entities

The integration exposes these sensors:

- `sensor.todays_album`
- `sensor.todays_artist`
- `sensor.todays_cover_art`

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
- This uses the public project endpoint at `https://1001albumsgenerator.com/api/v1/projects/patrick-curtain`.
- There is no auth key required.

## Validation

```bash
python -m unittest tests/test_parser.py -v
```
