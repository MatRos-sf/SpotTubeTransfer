from dataclasses import dataclass
from typing import List


@dataclass
class Artist:
    name: str


@dataclass
class Track:
    title: str
    artists: List[Artist]

    def __str__(self):
        return f"{self.title} by {', '.join(artist.name for artist in self.artists)}"


@dataclass
class Playlist:
    name: str
    description: str
    items: List[Track]

    @property
    def songs(self) -> int:
        return len(self.items)
