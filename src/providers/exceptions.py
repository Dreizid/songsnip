class ProviderError(Exception):
    """Base exception for all scraping related errors."""

    pass


class TrackMetadataError(ProviderError):
    """Raised when the track metadata is missing."""

    pass


class LyricsNotFoundError(ProviderError):
    """Raised when the lyrics for the track is missing."""

    pass
