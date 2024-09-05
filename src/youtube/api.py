from abc import ABC, abstractmethod

import google_auth_oauthlib.flow as google_auth
import googleapiclient.discovery as google_client

from src.youtube.search import YTSearch


class YouTubeOperation(ABC):
    @abstractmethod
    def insert(self, *args, **kwargs):
        pass


class Playlists(YouTubeOperation):
    INSERT_QUOTA_COST = 50

    def __init__(self, client):
        self.youtube = client
        self.part = "snippet,status"
        self.id = None

    def insert(self, *args, **kwargs):
        body = {
            "snippet": {
                "title": kwargs.get("title", "Sample Playlist create via SpotTube."),
                "description": kwargs.get("description", "Just enjoy listening ;)"),
                "tags": [
                    "SpotTube playlist",
                ],
            },
            "status": {"privacyStatus": kwargs.get("status", "private")},
        }
        request = self.youtube.playlists().insert(part=self.part, body=body)
        response = request.execute()
        # set new ID
        self.id = response.get("id")
        return response


class PlayListItems(YouTubeOperation):
    def __init__(self, client):
        self.youtube = client
        self.part = "snippet"

    def insert(self, playlist_id, video_id):
        body = {
            "snippet": {
                "playlistId": playlist_id,
                "position": 0,
                "resourceId": {"kind": "youtube#video", "videoId": video_id},
            }
        }
        request = self.youtube.playListItems().insert(part=self.part, body=body)
        response = request.execute()

        return response


class Youtube:
    API_SERVICE_NAME = "youtube"
    API_VERSION = "v3"
    SCOPE = ["https://www.googleapis.com/auth/youtube.force-ssl"]

    def __init__(self, client_secret_file):
        self.secret_file = client_secret_file
        self.youtube = self._build_google_api_client()

        self.playlist = Playlists(self.youtube)
        self.playlist_items = PlayListItems(self.youtube)

    def _build_google_api_client(self):
        flow = google_auth.flow.InstalledAppFlow.from_client_secrets_file(
            self.secret_file, self.SCOPE
        )
        credentials = flow.run_local_server()

        return google_client.build(
            self.API_SERVICE_NAME, self.API_VERSION, credentials=credentials
        )

    def search_video_by_api(self, query):
        raise NotImplementedError

    def search_video_by_web_scraping(self, track, webdriver: str = "Chrome"):
        searcher = YTSearch(webdriver)
        return searcher.search_id(track)

    def create_playlist(self):
        pass
