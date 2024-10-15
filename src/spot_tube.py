from abc import ABC, abstractmethod
from typing import Dict

from googleapiclient.errors import HttpError
from pyfiglet import Figlet

from src.database.connection import STdb
from src.spotify.api import Spotify, SpotifyException
from src.youtube.api import Youtube

# from src.youtube.exception import ExceedQuotaException


def welcome_screen(app_name):
    def inner(func):
        def wrapper(*args, **kwargs):
            print("*" * 100)
            f = Figlet(font="slant")
            text = f.renderText(app_name)
            print(text)
            print("*" * 100)

            func(*args, **kwargs)

            print("*" * 100)

        return wrapper

    return inner


class ConsoleApp(ABC):
    def __init__(self, options: Dict[str, str]):
        """
        Attribute options should be a dictionary where key is prefix of the option and value is describe options.
        """
        self.options = options

    @abstractmethod
    def menu(self, option: str):
        raise NotImplementedError()

    @abstractmethod
    def run(self):
        raise NotImplementedError()

    def check_options(self) -> None:
        options = self.options.keys()

        for option in options:
            getattr(self, f"do_{option}")

    def print_option(self) -> None:
        print("\n\nOptions:")
        options = self.options.values()
        for i, option in enumerate(options, start=1):
            print(f"{i}. {option}")
        print("\n\n")


class SpotTube(ConsoleApp):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        credential_file_name: str,
        database: STdb,
    ):
        super(SpotTube, self).__init__(
            {"transfer": "Transfer playlist from Spotify to YouTube"}
        )
        try:
            self.check_options()
        except AttributeError as e:
            raise Exception(f"Please implement method: {e.name}") from e
        self.spotify = Spotify(client_id, client_secret)
        self.youtube = Youtube(credential_file_name)
        self.db = database

    def do_transfer(self, id_spotify_playlist) -> bool:
        # capture id of playlist
        try:
            playlist = self.spotify.capture_playlist(id_spotify_playlist)
        except SpotifyException:
            print(
                "Invalid ID of spotify playlist. Please check id of playlist and try again."
            )
            return False

        id_playlist = self.youtube.create_playlist(playlist)
        if not id_playlist:
            print("Failed to create playlist on YouTube.")
            return False

        for track in playlist.items:
            # 1st search on db
            search_result = self.db.search_track(track)
            if not search_result:
                youtube_id = self.youtube.search_video_by_web_scraping(track)
                self.db.add_track(track, youtube_id)
            else:
                track_id, youtube_id = search_result

            try:
                status_insert = self.youtube.add_track_to_playlist(
                    id_playlist, youtube_id
                )
            except HttpError as e:
                print(f"Failed to add track '{track}' to playlist: {e}")
                return False

            if status_insert:
                print(f"Track '{track}' has been added to playlist. ")
                if search_result:
                    self.db.update_upload(track_id)

        print(f"Playlist {playlist.name} has been successfully transferred to YouTube.")
        return True

    def menu(self, option: str) -> bool:
        try:
            option = int(option)
        except ValueError:
            print("Invalid option. Please enter a number.")
            return False
        funct_prefix = list(self.options.keys())[option - 1]
        opt_func = getattr(self, f"do_{funct_prefix}")

        match option:
            case 1:
                id_playlist = input("Tab spotify id playlist: ")
                return opt_func(id_playlist)
            case 2:
                # TODO: update song to playlist
                print("We are working for this options.")
            case 3:
                # TODO: load playlist for database
                print("We are working for this options.")

            case _:
                print("Please choose correct options")

    @welcome_screen(app_name="SpotTube")
    def run(self):
        while True:
            self.print_option()
            option = input("Chose an option: ")
            if option.upper() == "QUIT":
                break
            self.menu(option)
