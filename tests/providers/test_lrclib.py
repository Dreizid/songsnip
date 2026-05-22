import pytest
import requests
from requests.exceptions import HTTPError, RequestException

from src.providers.lrclib import LRCLibScraper
from src.providers.exceptions import LyricsNotFoundError, TrackMetadataError
from src.core.exceptions import ServiceUnavailableError
from src.core.types import ResolverType

from src.core.schema import TrackMetadata
from src.providers.base import LyricsData


def test_fetch_invalid_track():
    """I want to ensure empty tracks or missing titles immediately reject."""
    scraper = LRCLibScraper()

    with pytest.raises(TrackMetadataError):
        scraper.fetch(None)

    bad_track = TrackMetadata(title="", artist="Drake", resolver=ResolverType.DEEZER)
    with pytest.raises(TrackMetadataError):
        scraper.fetch(bad_track)


def test_fetch_routes_to_get_by_id(mocker):
    """I expect fetch to use the ID route if the resolver is LRCLIB and an ID exists."""
    scraper = LRCLibScraper()
    track = TrackMetadata(
        title="Hotline Bling", artist="Drake", resolver=ResolverType.LRCLIB, id=123
    )

    mock_get_by_id = mocker.patch.object(scraper, "_get_by_id", return_value="id_route")

    result = scraper.fetch(track)

    assert result == "id_route"
    mock_get_by_id.assert_called_once_with(track)


def test_fetch_routes_to_get_by_metadata(mocker):
    """I expect fetch to fallback to metadata search if it's not from LRCLIB or lacks an ID."""
    scraper = LRCLibScraper()

    track = TrackMetadata(
        title="Hotline Bling", artist="Drake", resolver=ResolverType.DEEZER, id=123
    )

    mock_get_by_meta = mocker.patch.object(
        scraper, "_get_by_metadata", return_value="meta_route"
    )

    result = scraper.fetch(track)

    assert result == "meta_route"
    mock_get_by_meta.assert_called_once_with(track)


def test_get_by_id_flow(mocker):
    """I want to verify the ID flow calls the network and mapper correctly."""

    scraper = LRCLibScraper()
    track = TrackMetadata(
        title="Test", artist="Artist", resolver=ResolverType.LRCLIB, id=999
    )

    mock_request = mocker.patch.object(
        scraper, "_request", return_value={"raw": "data"}
    )
    mock_map = mocker.patch.object(
        scraper, "_map_to_lyrics", return_value=LyricsData(text="lyrics")
    )

    result = scraper._get_by_id(track)

    mock_request.assert_called_once_with("/api/get/999", params=None, context="Test")
    mock_map.assert_called_once_with({"raw": "data"})
    assert result.text == "lyrics"


def test_get_by_metadata_strips_none_params(mocker):
    """I expect the metadata flow to build a clean query dict without None values."""
    scraper = LRCLibScraper()

    track = TrackMetadata(title="Test", artist="Artist", resolver=ResolverType.DEEZER)

    mock_request = mocker.patch.object(scraper, "_request", return_value={})
    mocker.patch.object(scraper, "_map_to_lyrics")

    scraper._get_by_metadata(track)

    expected_params = {"track_name": "Test", "artist_name": "Artist"}

    mock_request.assert_called_once_with("/api/get", expected_params, "Test")


def test_request_success(mocker):
    """I expect a 200 OK to return the parsed JSON dictionary."""
    scraper = LRCLibScraper()

    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True}

    mocker.patch("src.providers.lrclib.requests.get", return_value=mock_response)

    result = scraper._request("/test", params={"q": 1}, context="Context")

    assert result == {"success": True}


def test_request_404_not_found(mocker):
    """I expect a 404 to raise my custom LyricsNotFoundError."""
    scraper = LRCLibScraper()

    mock_response = mocker.Mock()
    mock_response.status_code = 404

    mocker.patch("src.providers.lrclib.requests.get", return_value=mock_response)

    with pytest.raises(LyricsNotFoundError) as exc:
        scraper._request("/test", params=None, context="MyTrack")

    assert "MyTrack" in str(exc.value)


def test_request_5xx_server_error(mocker):
    """I expect server crashes to map to ServiceUnavailableError."""
    scraper = LRCLibScraper()

    mock_response = mocker.Mock()
    mock_response.status_code = 503

    http_err = HTTPError("503 Error")
    http_err.response = mock_response
    mock_response.raise_for_status.side_effect = http_err

    mocker.patch("src.providers.lrclib.requests.get", return_value=mock_response)

    with pytest.raises(ServiceUnavailableError):
        scraper._request("/test", params=None, context="Ctx")


def test_request_other_http_error(mocker):
    """I expect non-404/non-5xx errors (like 400 or 401) to just raise HTTPError."""
    scraper = LRCLibScraper()

    mock_response = mocker.Mock()
    mock_response.status_code = 400

    http_err = HTTPError("400 Bad Request")
    http_err.response = mock_response
    mock_response.raise_for_status.side_effect = http_err

    mocker.patch("src.providers.lrclib.requests.get", return_value=mock_response)

    with pytest.raises(HTTPError):
        scraper._request("/test", params=None, context="Ctx")


def test_request_connection_drop(mocker):
    """I expect hard network failures to map to ServiceUnavailableError."""
    scraper = LRCLibScraper()

    mocker.patch(
        "src.providers.lrclib.requests.get", side_effect=RequestException("No internet")
    )

    with pytest.raises(ServiceUnavailableError):
        scraper._request("/test", params=None, context="Ctx")


def test_map_to_lyrics_missing_data():
    """I expect validation to fail if LRCLib returns an empty payload."""
    scraper = LRCLibScraper()

    with pytest.raises(LyricsNotFoundError):
        scraper._map_to_lyrics({"trackName": "Only Title"})

    with pytest.raises(LyricsNotFoundError):
        scraper._map_to_lyrics({"plainLyrics": "Only Lyrics"})


def test_map_to_lyrics_success():
    """I expect a valid payload to correctly assemble a LyricsData object."""
    scraper = LRCLibScraper()

    payload = {
        "trackName": "Never Catch Me",
        "plainLyrics": "I can see the darkness",
        "syncedLyrics": "[00:10.00] I can see the darkness",
    }

    result = scraper._map_to_lyrics(payload)

    assert result.title == "Never Catch Me"
    assert result.text == "I can see the darkness"
    assert result.synced_text == "[00:10.00] I can see the darkness"
    assert result.source == ResolverType.LRCLIB.value


def test_map_to_lyrics_no_synced_text():
    """I want to ensure missing synced lyrics map cleanly to None."""
    scraper = LRCLibScraper()

    payload = {
        "trackName": "Instrumental Track",
        "plainLyrics": "Ooh ooh",
        "syncedLyrics": "",
    }

    result = scraper._map_to_lyrics(payload)

    assert result.text == "Ooh ooh"
    assert result.synced_text is None
