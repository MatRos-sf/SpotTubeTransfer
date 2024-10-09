from collections import Counter

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

    def get_or_create(self, session, model, **kwargs):
        instance = session.query(model).filter_by(**kwargs).first()
        if instance:
            print(f"Instance of {model.__name__} already exists: {kwargs}")
            return instance
        else:
            instance = model(**kwargs)
            session.add(instance)
            return instance


class STdb:
    def __init__(self, db_name="sqlite:///spotTube.db"):
        self.db = Database(db_name)

    def search_track(self, track: SpotifyTrack):
        """
        Methods to search a track. When a track is found it will be returned the tuple of (id, youtube_id) track. Otherwise it will be None.
        Args:
            track (SpotifyTrack):       The track to search.
        Returns:
            Optional[Tuple[int, str]]:  The tuple of id and youtube_id track if found, otherwise None.
        """
        artists = track.extract_artists()
        with self.db as session:
            # find all track with the particular title and whose artists are available
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

    def add_track(self, track: SpotifyTrack, youtube_id: str) -> None:
        """
        Methods to add a new track

        Args:
            track (SpotifyTrack):       The track to add.
            youtube_id (str):           The YouTube video id of the track.
        Returns:
            None
        """
        with self.db as session:
            artists = [
                self.db.get_or_create(session, Artist, name=art.name)
                for art in track.artists
            ]

            track = Track(title=track.title, youtube_id=youtube_id)
            track.artists.extend([*artists])
            session.add(track)

    def update_upload(self, pk: int) -> None:
        with self.db as session:
            track = session.query(Track).filter(Track.id == pk).first()
            track.uploaded += 1


# Przykład użycia:

song1 = SpotifyTrack(
    title="I Don't Care",
    artists=[SpotifyArtist(name="Ed Sheeran"), SpotifyArtist(name="Justin Bieber")],
)

song2 = SpotifyTrack(title="I Don't Care", artists=[SpotifyArtist(name="Ed Sheeran")])
#
stdb = STdb()
# print(stdb.search_track(song1))
#
# Dodaj pierwszy utwór
# stdb.add_track(song1, "y83x7MgzWOA")

# Dodaj drugi utwór
# stdb.add_track(song2, "ymjNGjuBCTo")

pk, _ = stdb.search_track(song2)
stdb.update_upload(pk)
