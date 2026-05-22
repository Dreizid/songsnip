import pytest

from src.core.schema import LyricsData, TrackMetadata
from src.core.types import ResolverType


def test_lyrics_data_defaults():
    """I want to verify that a LyricsData instance sets up its optional defaults properly."""
    lyrics = LyricsData(text="Just regular unsynced text lines.")

    assert lyrics.text == "Just regular unsynced text lines."
    assert lyrics.synced_text is None
    assert lyrics.title == ""
    assert lyrics.source == ""


def test_lyrics_data_is_synced_property_false():
    lyrics = LyricsData(text="Unsynced lyrics stream.")

    assert lyrics.is_synced is False


def test_lyrics_data_is_synced_property_true():
    """I expect is_synced to return True when synced_text contains timestamp strings."""
    lyrics = LyricsData(
        text="[00:12] Line one", synced_text="[00:12.50] Line one\n[00:15.00] Line two"
    )

    assert lyrics.is_synced is True


def test_track_metadata_creation_success():
    metadata = TrackMetadata(
        title="Bohemian Rhapsody",
        artist="Queen",
        resolver=ResolverType.DEEZER,
        id=1109731,
        album="A Night at the Opera",
        duration=354,
        isrc="GBARL6500018",
    )

    # Assert
    assert metadata.title == "Bohemian Rhapsody"
    assert metadata.artist == "Queen"
    assert metadata.resolver == ResolverType.DEEZER
    assert metadata.id == 1109731
    assert metadata.album == "A Night at the Opera"
    assert metadata.duration == 354
    assert metadata.isrc == "GBARL6500018"


def test_track_metadata_optional_fields_default_to_none():
    """I want to ensure that minimal track info leaves detailed keys as None."""
    metadata = TrackMetadata(
        title="Under Pressure", artist="Queen", resolver=ResolverType.DEEZER
    )

    # Assert
    assert metadata.id is None
    assert metadata.album is None
    assert metadata.duration is None
    assert metadata.isrc is None
