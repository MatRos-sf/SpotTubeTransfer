import re
from typing import Optional

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.spotify.models import Track
from src.youtube.exception import VideoNotFoundException


class WebdriverFactory:
    def __init__(self, driver):
        self.driver = driver

    @classmethod
    def create_webdriver(cls, name_driver: str) -> "WebdriverFactory":
        match name_driver.upper():
            case "CHROME":
                chrome_options = Options()
                # run the chrome without the GUI
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--disable-gpu")
                return WebdriverFactory(webdriver.Chrome(options=chrome_options))
            case _:
                raise ValueError(f"Unsupported driver name: {name_driver}")


class UrlBuilder:
    def __init__(self, base_url: str = "https://www.youtube.com/results?search_query="):
        self.base_url = base_url

    def build(self, track: Track):
        authors = "+".join([artist.name.replace(" ", "+") for artist in track.artists])
        title = track.title.replace(" ", "+")
        search_query = "+".join(filter(None, [authors, title]))
        return f"{self.base_url}{search_query}"


class YTSearch:
    SEARCH_PATTERN = re.compile(r"https\:\/\/www\.youtube.com\/watch\?v\=(.*)&pp=.*")

    def __init__(self, webdriver_name: Optional[str] = "Chrome"):
        self.driver = WebdriverFactory.create_webdriver(webdriver_name).driver
        self.url_builder = UrlBuilder()

    def find_id_by_href(self, href) -> str:
        match = self.SEARCH_PATTERN.search(href)
        if match:
            return match.group(1)
        raise ValueError("Invalid YouTube URL")

    def search_id(self, track: Track) -> str:
        url = self.url_builder.build(track)
        self.driver.get(url)

        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div#contents ytd-video-renderer")
                )
            )
        except TimeoutException:
            raise VideoNotFoundException("No video found within the time limit.")

        # Try to find any content
        contents = self.driver.find_elements(
            By.CSS_SELECTOR, "div#contents ytd-video-renderer"
        )

        for content in contents:
            title_element = content.find_element(By.CSS_SELECTOR, "a#video-title")
            href = title_element.get_attribute("href")
            if href:
                return self.find_id_by_href(href)

        raise VideoNotFoundException("No suitable video found.")
