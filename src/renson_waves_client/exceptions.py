"""Exceptions for renson-waves-client."""


class RensonWavesError(Exception):
    """Base exception for all Renson WAVES errors."""


class RensonWavesCannotConnect(RensonWavesError):
    """Raised when a connection to the device cannot be established.

    This is used by :meth:`~renson_waves_client.RensonWavesClient.async_get_constellation`
    to signal that the host is unreachable or the port is not open.
    """


class RensonWavesRequestError(RensonWavesError):
    """Raised when an HTTP request fails with a non-2xx status code,
    or when a network error occurs during a *strict-mode* endpoint call.
    """


class RensonWavesResponseError(RensonWavesError):
    """Raised when a response cannot be decoded as valid JSON."""
