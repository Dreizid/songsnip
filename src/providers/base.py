from abc import ABC, abstractmethod
from src.core.schema import LyricsData

from src.resolvers.base import TrackMetadata


class BaseScraper(ABC):
    """Abstract class for every lyric provider"""

    BASE_URL: str

    @abstractmethod
    def fetch(self, track: TrackMetadata) -> LyricsData:
        pass
