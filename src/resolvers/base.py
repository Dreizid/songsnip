from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.core.types import ResolverType


@dataclass
class TrackMetadata:
    title: str
    artist: str
    resolver: ResolverType
    id: int | None = None
    album: str | None = None
    duration: int | None = None
    isrc: str | None = None


class BaseResolver(ABC):
    """
    The blueprint for all metadata extraction service.
    """

    BASE_URL: str
    RESOLVER_TYPE: ResolverType

    @abstractmethod
    def resolve(self, query: str) -> TrackMetadata:
        """
        Parses a raw string to find matching track information.

        Args:
            query: A messy string (e.g., 'Drake - Hotline Bling.mp3')

        Returns:
            A TrackMetadata object containing the best match.

        Raises:
            InvalidQueryError: If the query is empty, too short, or contains unsupported characters.
            TrackNotFoundError: If the service is reachable but no matching track exist for the query.
            ServiceUnavailableError: If the remote API is down or timing out.
            ResolverError: For any other unexpected errors specific to the resolution logic.
        """
        pass
