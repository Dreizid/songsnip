import pytest
import requests
from requests.exceptions import HTTPError, RequestException


from src.resolvers.deezer import DeezerResolver
from src.resolvers.exceptions import (
    InvalidQueryError,
    TooManyRequestError,
    TrackNotFoundError,
)
from src.core.exceptions import ServiceUnavailableError
from src.core.types import ResolverType
from src.core.schema import TrackMetadata


def test_search_empty_query():
    resolver = DeezerResolver()

    with pytest.raises(InvalidQueryError):
        resolver.search("")


def test_search_success_with_data(mocker):
    resolver = DeezerResolver()

    mock_payload = {
        "data": [
            {
                "id": 12345,
                "title": "Starboy",
                "artist": {"name": "The Weeknd"},
                "album": {"title": "Starboy"},
                "duration": 230,
                "isrc": "USUG11601736",
            }
        ]
    }

    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_payload

    mocker.patch("src.resolvers.deezer.requests.get", return_value=mock_response)

    results = resolver.search("Starboy")

    assert len(results) == 1
    track = results[0]
    assert isinstance(track, TrackMetadata)
    assert track.title == "Starboy"
    assert track.artist == "The Weeknd"
    assert track.id == 12345
    assert track.resolver == ResolverType.DEEZER


def test_search_success_empty_data(mocker):
    resolver = DeezerResolver()

    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": []}

    mocker.patch("src.resolvers.deezer.requests.get", return_value=mock_response)

    results = resolver.search("NonExistentTrack123")
    assert results == []


def test_search_rate_limit(mocker):
    resolver = DeezerResolver()

    mock_response = mocker.Mock()
    mock_response.status_code = 429

    mocker.patch("src.resolvers.deezer.requests.get", return_value=mock_response)

    with pytest.raises(TooManyRequestError):
        resolver.search("Any query")


def test_search_server_error(mocker):
    resolver = DeezerResolver()

    mock_response = mocker.Mock()
    mock_response.status_code = 503

    http_err = HTTPError("503 Server Error")
    http_err.response = mock_response
    mock_response.raise_for_status.side_effect = http_err

    mocker.patch("src.resolvers.deezer.requests.get", return_value=mock_response)

    with pytest.raises(ServiceUnavailableError):
        resolver.search("Crash the server")


def test_search_other_http_error(mocker):
    resolver = DeezerResolver()

    mock_response = mocker.Mock()
    mock_response.status_code = 400

    http_err = HTTPError("400 Bad Request")
    http_err.response = mock_response
    mock_response.raise_for_status.side_effect = http_err

    mocker.patch("src.resolvers.deezer.requests.get", return_value=mock_response)

    with pytest.raises(HTTPError):
        resolver.search("Bad query")


def test_search_connection_drop(mocker):
    resolver = DeezerResolver()

    mocker.patch(
        "src.resolvers.deezer.requests.get",
        side_effect=RequestException("Connection aborted."),
    )

    with pytest.raises(ServiceUnavailableError):
        resolver.search("Connection drop test")


def test_resolve_success(mocker):
    resolver = DeezerResolver()

    mock_track_1 = TrackMetadata(
        title="First", artist="Artist", resolver=ResolverType.DEEZER
    )
    mock_track_2 = TrackMetadata(
        title="Second", artist="Artist", resolver=ResolverType.DEEZER
    )

    mocker.patch.object(resolver, "search", return_value=[mock_track_1, mock_track_2])

    result = resolver.resolve("Does not matter")

    assert result == mock_track_1


def test_resolve_not_found(mocker):
    resolver = DeezerResolver()

    mocker.patch.object(resolver, "search", return_value=[])

    with pytest.raises(TrackNotFoundError):
        resolver.resolve("Ghost track")
