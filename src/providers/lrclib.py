from src.core.exceptions import ServiceUnavailableError
from .exceptions import LyricsNotFoundError, TrackMetadataError
from .base import BaseScraper, LyricsData
from urllib import parse
import requests
from requests.exceptions import HTTPError, RequestException

from src.core.types import ResolverType
from src.core.schema import TrackMetadata


class LRCLibScraper(BaseScraper):
    BASE_URL = "https://lrclib.net"

    def fetch(self, track: TrackMetadata):
        if not track or not track.title:
            raise TrackMetadataError

        if track.resolver == ResolverType.LRCLIB and track.id:
            return self._get_by_id(track)
        else:
            return self._get_by_metadata(track)

    def _get_by_id(self, track: TrackMetadata) -> LyricsData:
        data = self._request(f"/api/get/{track.id}", params=None, context=track.title)
        return self._map_to_lyrics(data)

    def _get_by_metadata(self, track: TrackMetadata) -> LyricsData:
        raw_params = {
            "track_name": track.title,
            "artist_name": track.artist,
            "album_name": track.album,
            "duration": track.duration,
        }

        params = {k: v for k, v in raw_params.items() if v is not None}

        data = self._request("/api/get", params, track.title)

        return self._map_to_lyrics(data)

    def _request(self, endpoint: str, params: dict | None, context: str) -> dict:
        full_url = parse.urljoin(self.BASE_URL, endpoint)
        try:
            response = requests.get(full_url, params=params)

            if response.status_code == 404:
                raise LyricsNotFoundError(
                    f"Could not find lyrics for track name {context}"
                )

            response.raise_for_status()
        except HTTPError as e:
            if 500 < e.response.status_code < 600:
                raise ServiceUnavailableError("LRCLib is having a problem") from e

            raise e

        except RequestException as e:
            raise ServiceUnavailableError("Could not reach LRCLib") from e

        return response.json()

    def _map_to_lyrics(self, data: dict[str, str]) -> LyricsData:
        title = data.get("trackName")
        artist = data.get("artistName", "Unknown Artist")
        plain_text = data.get("plainLyrics")
        synced_text = data.get("syncedLyrics")

        if not title or not plain_text:
            raise LyricsNotFoundError(
                f"API returned empty content for title '{title}' by {artist}"
            )

        return LyricsData(
            title=title,
            artist=artist,
            text=plain_text,
            synced_text=synced_text or None,
            source=ResolverType.LRCLIB.value,
        )
