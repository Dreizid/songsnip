class ResolverError(Exception):
    """
    Base exception for all metadata resolution issues.
    """

    pass


class InvalidQueryError(ResolverError):
    """
    Raised when the input string contains illegal characters or is empty.
    """

    pass


class TrackNotFoundError(ResolverError):
    """
    Raised when the service is up, but no track matches the query.
    """

    pass


class TooManyRequestError(ResolverError):
    """
    Raised when we hit API rate limits (HTTP 429).
    """
