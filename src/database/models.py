from typing import List

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship

Base = declarative_base()

association_table = sa.Table(
    "association_table",
    Base.metadata,
    sa.Column("artist_id", sa.Integer, sa.ForeignKey("artist_table.id")),
    sa.Column("track_id", sa.Integer, sa.ForeignKey("track_table.id")),
)


class Artist(Base):
    __tablename__ = "artist_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    tracks: Mapped[List["Track"]] = relationship(
        "Track", secondary=association_table, back_populates="artists"
    )

    def __repr__(self):
        return f"Artist(id={self.id}, name={self.name})"


class Track(Base):
    __tablename__ = "track_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    artists: Mapped[List["Artist"]] = relationship(
        "Artist", secondary=association_table, back_populates="tracks"
    )

    def __repr__(self):
        return f"Track(id={self.id}, title={self.title})"
