from unittest.mock import MagicMock, patch

import pytest
from selenium import webdriver

from src.spotify.models import Artist, Track
from src.youtube.exception import VideoNotFoundException
from src.youtube.search import UrlBuilder, WebdriverFactory, YTSearch

SAMPLE_TRACK = Track("Never Gonna Give You Up", [Artist("Rick Astley")])


class TestWebdriverFactory:
    def test_create_chrome_webdriver(self):
        driver_factory = WebdriverFactory.create_webdriver("Chrome")
        assert isinstance(driver_factory.driver, webdriver.Chrome)

    def test_create_unsupported_webdriver(self):
        with pytest.raises(ValueError, match="Unsupported driver name: UNSUPPORTED"):
            WebdriverFactory.create_webdriver("UNSUPPORTED")


class TestSearchUrlBuilder:
    def test_builder_should_create_url(self):
        expected_url = "https://www.youtube.com/results?search_query=Rick+Astley+Never+Gonna+Give+You+Up"
        url_builder = UrlBuilder()
        url = url_builder.build(SAMPLE_TRACK)
        assert url == expected_url

    def test_builder_should_return_empty_search_query(self):
        track = Track("", [])
        url_builder = UrlBuilder()
        url = url_builder.build(track)
        assert url == "https://www.youtube.com/results?search_query="

    @pytest.mark.parametrize(
        "track, expected_url",
        [
            (
                Track("Never Gonna Give You Up", []),
                "https://www.youtube.com/results?search_query=Never+Gonna+Give+You+Up",
            ),
            (
                Track("", [Artist("Rick Astley")]),
                "https://www.youtube.com/results?search_query=Rick+Astley",
            ),
        ],
    )
    def test_builder_should_return_correct_url_when_one_value_is_empty(
        self, track, expected_url
    ):
        url_builder = UrlBuilder()
        url = url_builder.build(track)
        assert url == expected_url


class TestYTSearch:
    def test_find_id_by_href_should_raise_value_error_when_href_does_not_match_pattern(
        self,
    ):
        searcher = YTSearch()
        with pytest.raises(ValueError) as e:
            searcher.find_id_by_href("https://www.youtube.com/watch?v=invalid_id")
        assert str(e.value) == "Invalid YouTube URL"

    def test_search_id_should_return_yt_id(self):
        expected = "dQw4w9WgXcQ"
        searcher = YTSearch()
        id = searcher.search_id(SAMPLE_TRACK)
        assert id == expected

    @patch("src.youtube.search.WebdriverFactory")
    def test_search_id_should_raise_video_not_found_error(self, mock_ytsearch):
        mock_driver = MagicMock()
        mock_driver.return_value.driver.driver = mock_driver
        mock_driver.find_elements.return_value = []

        searcher = YTSearch()
        with pytest.raises(VideoNotFoundException) as e:
            searcher.search_id(SAMPLE_TRACK)

        assert str(e.value) == "No suitable video found."
