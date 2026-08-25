"""Constants for the 1001 Albums integration."""

DOMAIN = "one_thousand_one_albums"
API_BASE_URL = "https://1001albumsgenerator.com/api/v1/projects"
DEFAULT_PROJECT = "patrick-curtain"
CONF_PROJECT = "project"


def build_project_url(project: str) -> str:
    """Convert a project slug to the public JSON API URL."""
    slug = (project or DEFAULT_PROJECT).strip().strip("/")
    return f"{API_BASE_URL}/{slug}"
