from src.core.types import ResolverType
from .base import BaseResolver, TrackMetadata
from .exceptions import InvalidQueryError, TooManyRequestError, TrackNotFoundError
import requests
from requests.exceptions import HTTPError, RequestException
from urllib import parse

from src.core.exceptions import ServiceUnavailableError


class DeezerResolver(BaseResolver):
    BASE_URL = "https://api.deezer.com"
    RESOLVER_TYPE = ResolverType.DEEZER

    def search(self, query: str) -> list[TrackMetadata]:
        """
        Parses raw string to find relevant tracks.

        Args:
            query: A messy string (e.g., 'Drake - Hotline Bling.mp3')

        Returns:
            A list of TrackMetadata objects.

        Raises:

        """
        if not query:
            raise InvalidQueryError

        end_point = "/search/track"
        params = {"q": query}
        full_url = parse.urljoin(self.BASE_URL, end_point)
        try:
            response = requests.get(full_url, params=params, timeout=10)

            if response.status_code == 429:
                raise TooManyRequestError
            response.raise_for_status()
        except HTTPError as e:
            if 500 <= e.response.status_code < 600:
                raise ServiceUnavailableError

            raise e
        except RequestException as e:
            raise ServiceUnavailableError from e

        data = response.json()
        data = data.get("data", [])

        return [
            TrackMetadata(
                title=item.get("title"),
                artist=item.get("artist", {}).get("name"),
                resolver=self.RESOLVER_TYPE,
                album=item.get("album", {}).get("title", ""),
                duration=item.get("duration", None),
                isrc=item.get("isrc", ""),
                id=item.get("id"),
            )
            for item in data
        ]

    def resolve(self, query: str):
        results = self.search(query)

        if not results:
            raise TrackNotFoundError

        return results[0]
