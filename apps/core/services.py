import logging
import re

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


def text_color_for_bg(hex_color: str) -> str:
    """Retourne '#1f2937' (dark) ou '#ffffff' (white) selon la luminance du fond."""
    try:
        r = int(hex_color[:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return "#1f2937" if luminance > 0.5 else "#ffffff"
    except (ValueError, IndexError):
        return "#1f2937"


def fetch_github_issues() -> tuple[list[dict], bool]:
    """Recupere les issues GitHub depuis le cache ou l'API.

    Returns:
        Un tuple (issues, api_error) ou issues est la liste des issues
        et api_error indique si une erreur API s'est produite.
    """
    issues = cache.get("github_issues")
    if issues is not None:
        return issues, False

    api_error = False
    try:
        url = f"{settings.GITHUB_REPO_API_URL}/issues?state=open&per_page=100"
        headers = {"Accept": "application/vnd.github.v3+json"}
        token = getattr(settings, "GITHUB_API_TOKEN", "")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            issues = [
                {
                    "title": issue["title"],
                    "labels": [
                        {
                            "name": label["name"],
                            "color": label["color"]
                            if re.match(
                                r"^[0-9a-fA-F]{6}$",
                                label.get("color", ""),
                            )
                            else "cccccc",
                            "text_color": text_color_for_bg(
                                label.get("color", "")
                            ),
                        }
                        for label in issue.get("labels", [])
                    ],
                }
                for issue in response.json()
            ]
            cache.set("github_issues", issues, timeout=300)
        else:
            logger.warning(
                "GitHub API returned status %s", response.status_code
            )
            api_error = True
    except requests.RequestException as exc:
        logger.warning("GitHub API request failed: %s", exc)
        api_error = True

    return issues or [], api_error
