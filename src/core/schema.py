from dataclasses import dataclass
from .types import ResolverType


@dataclass
class LyricsData:
    """The standard output of any lyric provider"""

    text: str
    synced_text: str | None = None
    title: str = ""
    source: str = ""

    @property
    def is_synced(self) -> bool:
        return self.synced_text is not None


@dataclass
class TrackMetadata:
    title: str
    artist: str
    resolver: ResolverType
    id: int | None = None
    album: str | None = None
    duration: int | None = None
    isrc: str | None = None
