import hashlib
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

    @property
    def track_id(self) -> str:
        if self.isrc and self.isrc.strip():
            return self.isrc.strip().upper()

        normalized = f"{self.artist.strip()}|{self.title.strip()}".lower()
        return hashlib.md5(normalized.encode("utf-8")).hexdigest()
