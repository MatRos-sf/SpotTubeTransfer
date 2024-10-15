from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import google_auth_oauthlib.flow as google_auth
import googleapiclient.discovery as google_client
from googleapiclient.errors import HttpError

from src.youtube.exception import ExceedQuotaException
from src.youtube.search import YTSearch

from ..spotify.models import Playlist


class YouTubeOperation(ABC):
    @abstractmethod
    def insert(self, *args, **kwargs):
        pass

    def execute(self, request) -> Optional[Dict[str, Any]]:
        try:
            response = request.execute()
        except HttpError:
            return None
        return response


class Playlists(YouTubeOperation):
    INSERT_QUOTA_COST = 50

    def __init__(self, client):
        self.youtube = client
        self.part = "snippet,status"
        self.id = None

    def insert(self, *args, **kwargs) -> Optional[Dict[str, Any]]:
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

        response = self.execute(request)
        # if response is successful, it will set id
        if response:
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
        request = self.youtube.playlistItems().insert(part=self.part, body=body)
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
        flow = google_auth.InstalledAppFlow.from_client_secrets_file(
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

    def create_playlist(self, playlist: Playlist) -> Optional[str]:
        # create playlist
        try:
            response = self.playlist.insert(
                title=playlist.name, description=playlist.description
            )
        except HttpError:
            response = None

        return response.get("id") if response else None

    def add_tracks_to_playlist(self, playlist_id, playlist: Playlist) -> None:
        for track in playlist.items:
            video_id = self.search_video_by_web_scraping(track)
            # create request to YouTube api and add song
            print(f"\t Adding song: {track} ", end="")
            song = self.playlist_items.insert(playlist_id, video_id)
            if not song:
                raise ExceedQuotaException(
                    "The requested cannot be completed because you have exceeded the quota"
                )

    def add_track_to_playlist(self, playlist_id: str, youtube_id: str):
        song = self.playlist_items.insert(playlist_id, youtube_id)
        print(f"YT: {song}")
        return True if song else False
