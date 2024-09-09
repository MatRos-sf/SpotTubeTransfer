from dataclasses import dataclass
from typing import List


@dataclass
class Artist:
    name: str


@dataclass
class Track:
    title: str
    artists: List[Artist]


@dataclass
class Playlist:
    name: str
    description: str
    items: List[Track]

    @property
    def songs(self) -> int:
        return len(self.items)
