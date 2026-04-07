# Template-based view tests removed — views migrated to React SPA.
# API view tests are in test_api.py.
# Service-layer tests below are kept as they test core business logic.

from unittest.mock import MagicMock, patch

import pytest
import requests as requests_lib
from django.core.cache import cache

from apps.core.services import text_color_for_bg


def _mock_github_response(status_code=200, json_data=None):
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = json_data or []
    return mock


MOCK_ISSUES = [
    {
        "title": "Bug: fix login",
        "labels": [
            {"name": "bug", "color": "d73a4a"},
            {"name": "priority", "color": "0075ca"},
        ],
    },
    {
        "title": "Feature: add search",
        "labels": [],
    },
]


class TestTextColorForBg:
    def test_light_background_returns_dark_text(self):
        assert text_color_for_bg("ffffff") == "#1f2937"

    def test_dark_background_returns_white_text(self):
        assert text_color_for_bg("000000") == "#ffffff"

    def test_yellow_returns_dark_text(self):
        assert text_color_for_bg("ffff00") == "#1f2937"

    def test_dark_red_returns_white_text(self):
        assert text_color_for_bg("d73a4a") == "#ffffff"

    def test_text_color_for_bg_invalid_input(self):
        assert text_color_for_bg("xyz") == "#1f2937"
        assert text_color_for_bg("") == "#1f2937"
        assert text_color_for_bg("gg0000") == "#1f2937"


@pytest.mark.django_db
class TestFetchGithubIssuesService:
    def setup_method(self):
        cache.clear()

    @patch("apps.core.services.requests.get")
    def test_fetch_returns_issues(self, mock_get):
        mock_get.return_value = _mock_github_response(200, MOCK_ISSUES)
        issues, api_error = __import__(
            "apps.core.services", fromlist=["fetch_github_issues"]
        ).fetch_github_issues()
        assert len(issues) == 2
        assert issues[0]["title"] == "Bug: fix login"
        assert api_error is False

    @patch("apps.core.services.requests.get")
    def test_fetch_caches_result(self, mock_get):
        from apps.core.services import fetch_github_issues

        mock_get.return_value = _mock_github_response(200, MOCK_ISSUES)
        fetch_github_issues()
        fetch_github_issues()
        assert mock_get.call_count == 1

    @patch("apps.core.services.requests.get")
    def test_fetch_returns_error_on_failure(self, mock_get):
        from apps.core.services import fetch_github_issues

        mock_get.side_effect = requests_lib.ConnectionError("fail")
        issues, api_error = fetch_github_issues()
        assert issues == []
        assert api_error is True

    @patch("apps.core.services.requests.get")
    def test_negative_cache_on_api_error(self, mock_get):
        from apps.core.services import fetch_github_issues

        mock_get.side_effect = requests_lib.ConnectionError("fail")
        fetch_github_issues()
        assert mock_get.call_count == 1
        mock_get.side_effect = None
        mock_get.return_value = _mock_github_response(200, MOCK_ISSUES)
        issues, api_error = fetch_github_issues()
        assert mock_get.call_count == 1
        assert issues == []
        assert api_error is False
