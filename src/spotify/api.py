from http import HTTPStatus

import requests

from .models import Artist, Playlist, Track


class SpotifyException(Exception):
    """Raised when id of playlist is incorrect"""

    def __init__(self, message):
        super().__init__(message)
        self.message = message


class Spotify:
    TOKEN_URL = "https://accounts.spotify.com/api/token"  # nosec
    PLAYLIST_URL = "https://api.spotify.com/v1/playlists/"  # nosec

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = self.get_access_token()

    def get_access_token(self):
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        response = requests.post(self.TOKEN_URL, data=data, timeout=60)
        if response.status_code == HTTPStatus.OK:
            return response.json()["access_token"]
        elif response.status_code in [
            HTTPStatus.UNAUTHORIZED,
            HTTPStatus.FORBIDDEN,
            HTTPStatus.TOO_MANY_REQUESTS,
        ]:
            raise Exception("Authorization error: {}".format(response.status_code))
        else:
            raise Exception("An error occurred: {}".format(response.status_code))

    def capture_playlist(self, playlist_id: str) -> Playlist:
        # create headers
        headers = {"Authorization": "Bearer {}".format(self.access_token)}
        request = requests.get(
            self.PLAYLIST_URL + f"{playlist_id}", headers=headers, timeout=60
        )

        response = request.json()
        # check if response has status error
        if response.get("error"):
            raise SpotifyException("The ID of the playlist is incorrect.")

        tracks = []
        for item in response["tracks"]["items"]:
            title = item["track"]["name"]
            artists = [Artist(artist["name"]) for artist in item["track"]["artists"]]
            tracks.append(Track(title, artists))

        return Playlist(
            name=response.get("name", ""),
            description=response.get("description", ""),
            items=tracks,
        )
