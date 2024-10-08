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

    def add_track(self, track: SpotifyTrack):
        with self.db as session:
            artists = [
                self.db.get_or_create(session, Artist, name=art.name)
                for art in track.artists
            ]

            track = Track(title=track.title)
            track.artists.extend([*artists])
            session.add(track)
            # db.commit()


# Przykład użycia:

song1 = SpotifyTrack(
    title="I Don't Care",
    artists=[SpotifyArtist(name="Ed Sheeran"), SpotifyArtist(name="Justin Bieber")],
)

song2 = SpotifyTrack(title="I Don't Care", artists=[SpotifyArtist(name="Ed Sheeran")])

stdb = STdb()

# Dodaj pierwszy utwór
stdb.add_track(song1)

# Dodaj drugi utwór
stdb.add_track(song2)
