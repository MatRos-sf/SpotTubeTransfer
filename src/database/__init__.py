import sqlite3

from src.spotify.models import Artist, Track

MAIN_DB = "main_db.db"


class Database:
    def __init__(self, database_name):
        self.con = sqlite3.connect(database_name)
        self.cur = self.con.cursor()
        self.create_table()

    def create_table(self):
        raise NotImplementedError()


class SpotubeDB(Database):
    def __init__(self, database_name):
        super().__init__(database_name)

    def create_table(self):
        """
        Create tables:
        Artist:
            name: str

        Track:
            title: str
            FOREIGN KEY artist_id: int REFERENCES artist
        :return:
        """
        query = """
        CREATE TABLE IF NOT EXISTS artist(
        name TEXT
        );

        CREATE TABLE IF NOT EXISTS track(
            track_yt_id TEXT,
            title TEXT,
            added INTEGER
        );

        CREATE TABLE IF NOT EXISTS artist_track(
            artist_id INTEGER,
            track_id INTEGER,
            FOREIGN KEY(artist_id) REFERENCES artist(artist_id) ON DELETE CASCADE,
            FOREIGN KEY(track_id) REFERENCES track(track_id) ON DELETE CASCADE,
            PRIMARY KEY (artist_id, track_id)
        );
        """
        self.cur.executescript(query)
        self.con.commit()

    def add_artist(self, artist: Artist):
        self.cur.execute("INSERT INTO artist (name) VALUES (?)", (artist.name,))
        artist_id = self.cur.lastrowid
        self.con.commit()
        return artist_id

    def add_track(self, track: Track, yt_id: str):
        self.cur.execute(
            "INSERT INTO track (track_yt_id, title) VALUES (?, ?)", (yt_id, track.title)
        )
        track_id = self.cur.lastrowid
        self.con.commit()
        return track_id

    def add_artist_track(self, artist_id: int, track_id: int):
        self.cur.execute(
            "INSERT INTO artist_track (artist_id, track_id) VALUES (?,?)",
            (artist_id, track_id),
        )
        self.con.commit()


#     def search_song(self, artist_id, track_id):
#         query = """
#         SELECT
#         """
# s = SpotubeDB(MAIN_DB)
# a_1, a_2 = Artist('NLE Choppa'), Artist('2Rare')
# t = Track(title='DO IT AGAIN (feat. 2Rare)', artists=[a_1, a_2])
#
# q = """
#     SELECT track.track_yt_id FROM artist
#     FROM artist
#     JOIN artist_track ON artist.artist_id = artist_track.artist_id
#     JOIN track ON artist_track.track_id = track.track_id
#     WHERE track.title = ? AND a
#     """
