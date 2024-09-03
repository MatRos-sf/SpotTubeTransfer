from dataclasses import dataclass
from http import HTTPStatus
from typing import List

import requests


@dataclass
class Artist:
    name: str


@dataclass
class Track:
    title: str
    artists: List[Artist]


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

    def capture_playlist(self, playlist_id: str) -> List[Track]:
        # create headers
        headers = {"Authorization": "Bearer {}".format(self.access_token)}
        response = requests.get(
            self.PLAYLIST_URL + f"{playlist_id}/tracks", headers=headers, timeout=60
        )

        tracks = []
        for item in response.json()["items"]:
            title = item["track"]["name"]
            artists = [Artist(artist["name"]) for artist in item["track"]["artists"]]
            tracks.append(Track(title, artists))
        return tracks
