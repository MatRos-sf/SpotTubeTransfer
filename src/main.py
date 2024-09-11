import os

from dotenv import load_dotenv

from src.spotify.api import Spotify
from src.youtube.api import Youtube

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
YT_CREDENTIAL_FILE_NAME = os.getenv("YT_CREDENTIAL_FILE_NAME")

# sample
spoti = Spotify(CLIENT_ID, CLIENT_SECRET)

playlist = spoti.capture_playlist("2uEKh2R4Gw8CDtPvzU9Sge")
yt = Youtube(YT_CREDENTIAL_FILE_NAME)
print("Create Playlist")
id_playlist = yt.create_playlist(playlist)
print(id_playlist)

print("Add Tracks to Playlist")
yt.add_tracks_to_playlist(id_playlist, playlist)
