from dataclasses import dataclass
from src.core.types import ResolverType


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

    @property
    def lines(self) -> list[str]:
        return self.text.splitlines() if self.text else []

    @property
    def synced_lines(self) -> list[str]:
        return self.synced_text.splitlines() if self.synced_text else []


@dataclass
class TrackMetadata:
    title: str
    artist: str
    resolver: ResolverType
    id: int | None = None
    album: str | None = None
    duration: int | None = None
    isrc: str | None = None
