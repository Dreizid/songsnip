from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.resolvers.base import TrackMetadata


@dataclass
class LyricsData:
    """The standard output of any lyric provider"""

    text: str
    synced_text: str | None = None
    title: str = ""
    source: str = ""
    artist: str = ""

    @property
    def is_synced(self) -> bool:
        return self.synced_text is not None


class BaseScraper(ABC):
    """Abstract class for every lyric provider"""

    BASE_URL: str

    @abstractmethod
    def fetch(self, track: TrackMetadata) -> LyricsData:
        pass
