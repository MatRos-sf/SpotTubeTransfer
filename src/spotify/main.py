from dataclasses import dataclass
from typing import List


@dataclass
class Artist:
    name: str


@dataclass
class Track:
    title: str
    artists: List[Artist]
