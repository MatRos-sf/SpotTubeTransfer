from collections import Counter
from typing import Optional, Tuple

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.models import Artist, Base, Track
from src.spotify.models import Artist as SpotifyArtist
from src.spotify.models import Track as SpotifyTrack

Session = sessionmaker()


class Database:
    def __init__(self, db_name="sqlite:///spotTube.db"):
        self.engine = create_engine(db_name)

        self.__bind_engine(self.engine)
        Base.metadata.create_all(self.engine)

    def __bind_engine(self, engine):
        Base.metadata.bind = engine
        Session.configure(bind=engine)

    def __enter__(self):
        self.session = Session()
        return self.session

    def __exit__(self, exc_type, exc_val, traceback):
        if exc_type is not None:
            self.session.rollback()
        else:
            self.session.commit()
        self.session.close()


class ArtistManager:
    def get_or_create_artist(self, session: Session, artist_name: str) -> Artist:
        instance = session.query(Artist).filter_by(name=artist_name).first()
        if instance:
            return instance
        else:
            instance = Artist(name=artist_name)
            session.add(instance)
            return instance


class TrackManager:
    def __init__(self, artist_manager: ArtistManager):
        self.artist_manager = artist_manager

    def search_track(
        self, session: Session, track: SpotifyTrack
    ) -> Optional[Tuple[int, str]]:
        """
        Methods to search a track. When a track is found it will be returned the tuple of (id, youtube_id) track. Otherwise it will be None.
        Args:
            session:                    Session
            track (SpotifyTrack):       The track to search.
        Returns:
            Optional[Tuple[int, str]]:  The tuple of id and youtube_id track if found, otherwise None.
        """
        artists = track.extract_artists()
        track_query = (
            session.query(Track)
            .join(Track.artists)
            .filter(Artist.name.in_(artists), Track.title == track.title)
            .all()
        )
        main_artists = Counter(artists)
        # looking for track
        for music in track_query:
            track_artists = Counter([singer.name for singer in music.artists])
            if track_artists == main_artists:
                return music.id, music.youtube_id
        return None

    def add_track(
        self, session: Session, new_track: SpotifyTrack, youtube_id: str
    ) -> None:
        """
        Methods to add a new track
        Args:
            session:                    Session
            new_track (SpotifyTrack):       The track to add.
            youtube_id (str):           The YouTube video id of the track.
        Returns:
            None
        """
        artists = [
            self.artist_manager.get_or_create_artist(session, art.name)
            for art in new_track.artists
        ]

        new_track = Track(title=new_track.title, youtube_id=youtube_id)
        new_track.artists.extend([*artists])
        session.add(new_track)

    def update_upload(self, session: Session, pk: int) -> None:
        track = session.query(Track).filter(Track.id == pk).first()
        track.uploaded += 1


class STdb:
    def __init__(self, database: Database):
        self.db = database
        self.artist_manager = ArtistManager()
        self.track_manager = TrackManager(self.artist_manager)

    def search_track(self, track: SpotifyTrack) -> Optional[Tuple[int, str]]:
        with self.db as session:
            return self.track_manager.search_track(session, track)

    def add_track(self, new_track: SpotifyTrack, youtube_id: str):
        with self.db as session:
            self.track_manager.add_track(session, new_track, youtube_id)

    def update_upload(self, pk: int) -> None:
        with self.db as session:
            self.track_manager.update_upload(session, pk)


if __name__ == "__main__":
    song1 = SpotifyTrack(
        title="I Don't Care",
        artists=[SpotifyArtist(name="Ed Sheeran"), SpotifyArtist(name="Justin Bieber")],
    )

    song2 = SpotifyTrack(
        title="I Don't Care", artists=[SpotifyArtist(name="Ed Sheeran")]
    )
    #
    stdb = STdb(Database())
    # print(stdb.search_track(song1))
    #
    # Dodaj pierwszy utwór
    stdb.add_track(song1, "y83x7MgzWOA")

    # Dodaj drugi utwór
    stdb.add_track(song2, "ymjNGjuBCTo")

    pk, _ = stdb.search_track(song2)
    stdb.update_upload(pk)
