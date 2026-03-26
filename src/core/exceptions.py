class ServiceUnavailableError(Exception):
    """
    Raised when the remote API returns a 5xx error or a timeout occurs.
    """
