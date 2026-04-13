"""Async HTTP client for the Renson WAVES local API."""

from __future__ import annotations

import asyncio
import logging
from types import TracebackType
from typing import Any, cast

import aiohttp
from aiohttp import ClientError

from .const import (
    API_VERSION,
    DEFAULT_PORT,
    DEFAULT_TIMEOUT,
    ENDPOINT_CONSTELLATION,
    ENDPOINT_DECISION_BREEZE,
    ENDPOINT_DECISION_ROOM,
    ENDPOINT_DECISION_SILENT,
    ENDPOINT_GLOBAL_UPTIME,
    ENDPOINT_WIFI_STATUS,
)
from .exceptions import (
    RensonWavesCannotConnect,
    RensonWavesRequestError,
    RensonWavesResponseError,
)
from .models import WavesData

_LOGGER = logging.getLogger(__name__)


class RensonWavesClient:
    """Async client for the Renson WAVES local HTTP API.

    Usage::

        async with RensonWavesClient("192.168.1.100") as client:
            constellation = await client.async_get_constellation()
            data = await client.async_get_all()

    Args:
        host: Hostname or IP address of the WAVES device.
        port: TCP port of the WAVES API (default: 8000).
        session: Optional external :class:`aiohttp.ClientSession`.  When
            provided the caller is responsible for closing it.  When omitted
            the client creates and owns an internal session.
    """

    def __init__(
        self,
        host: str,
        port: int = DEFAULT_PORT,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        self._host = host
        self._port = port
        self._base_url = f"http://{host}:{port}/{API_VERSION}"
        self._timeout = aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
        self._session = session
        self._own_session: bool = session is None

    # ------------------------------------------------------------------
    # Session lifecycle
    # ------------------------------------------------------------------

    async def _get_session(self) -> aiohttp.ClientSession:
        """Return the active session, creating one lazily when needed."""
        if (session := self._session) is None:
            session = aiohttp.ClientSession()
            self._session = session
        return session

    async def close(self) -> None:
        """Close the internally managed session, if any.

        This is a no-op when the client was constructed with an external
        session — the caller is responsible for closing that session.
        """
        if self._own_session and self._session is not None:
            await self._session.close()
            self._session = None

    async def __aenter__(self) -> RensonWavesClient:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.close()

    # ------------------------------------------------------------------
    # Internal HTTP helper
    # ------------------------------------------------------------------

    async def _get(
        self,
        endpoint: str,
        *,
        probe: bool = False,
        strict: bool = True,
    ) -> dict[str, Any]:
        """Perform a GET against *endpoint* (relative to ``/v1/``).

        Args:
            endpoint: Path relative to the ``/v1/`` base URL.
            probe: When ``True``, network / client errors are re-raised as
                :exc:`~.exceptions.RensonWavesCannotConnect` regardless of
                *strict*.  Used only by :meth:`async_get_constellation`.
            strict: When ``True``, raise on non-2xx responses and JSON parse
                failures.  When ``False``, return an empty dict instead and
                log at *DEBUG* level.

        Returns:
            Parsed JSON response body as a plain dict.

        Raises:
            RensonWavesCannotConnect: Network / client error and
                ``probe=True``.
            RensonWavesRequestError: Non-2xx response (strict) or network
                error (strict, no probe).
            RensonWavesResponseError: JSON parse failure (strict).
        """
        url = f"{self._base_url}/{endpoint}"
        session = await self._get_session()
        try:
            async with session.get(url, timeout=self._timeout) as response:
                if not response.ok:
                    if strict:
                        raise RensonWavesRequestError(
                            f"HTTP {response.status} from {url}"
                        )
                    _LOGGER.debug(
                        "Non-2xx response (%s) from %s — returning empty dict",
                        response.status,
                        url,
                    )
                    return {}

                try:
                    data = cast(
                        dict[str, Any],
                        await response.json(content_type=None),
                    )
                    return data
                except Exception as exc:
                    if strict:
                        raise RensonWavesResponseError(
                            f"Failed to parse JSON from {url}: {exc}"
                        ) from exc
                    _LOGGER.debug("JSON parse error from %s: %s", url, exc)
                    return {}

        except (RensonWavesRequestError, RensonWavesResponseError):
            raise
        except (ClientError, TimeoutError) as exc:
            if probe:
                raise RensonWavesCannotConnect(
                    f"Cannot connect to Renson WAVES at {url}: {exc}"
                ) from exc
            if strict:
                raise RensonWavesRequestError(
                    f"Request failed for {url}: {exc}"
                ) from exc
            _LOGGER.debug("Request error for %s (non-strict) — returning empty dict: %s", url, exc)
            return {}

    # ------------------------------------------------------------------
    # Public API methods
    # ------------------------------------------------------------------

    async def async_get_constellation(self) -> dict[str, Any]:
        """Probe connectivity and return constellation data.

        This method always raises on failure and is the recommended way to
        test whether the device is reachable before setting up a coordinator.

        Returns:
            Parsed constellation JSON payload.

        Raises:
            RensonWavesCannotConnect: Device is unreachable.
            RensonWavesRequestError: Device returned a non-2xx status.
            RensonWavesResponseError: Response is not valid JSON.
        """
        return await self._get(ENDPOINT_CONSTELLATION, probe=True, strict=True)

    async def async_get_wifi_status(self, *, strict: bool = False) -> dict[str, Any]:
        """Return WiFi client status.

        Args:
            strict: When ``True``, raise on failure.  Default ``False``.
        """
        return await self._get(ENDPOINT_WIFI_STATUS, strict=strict)

    async def async_get_global_uptime(self, *, strict: bool = False) -> dict[str, Any]:
        """Return global uptime data.

        Args:
            strict: When ``True``, raise on failure.  Default ``False``.
        """
        return await self._get(ENDPOINT_GLOBAL_UPTIME, strict=strict)

    async def async_get_decision_room(self, *, strict: bool = False) -> dict[str, Any]:
        """Return room-decision data.

        Args:
            strict: When ``True``, raise on failure.  Default ``False``.
        """
        return await self._get(ENDPOINT_DECISION_ROOM, strict=strict)

    async def async_get_decision_silent(
        self, *, strict: bool = False
    ) -> dict[str, Any]:
        """Return silent-mode decision data.

        Args:
            strict: When ``True``, raise on failure.  Default ``False``.
        """
        return await self._get(ENDPOINT_DECISION_SILENT, strict=strict)

    async def async_get_decision_breeze(
        self, *, strict: bool = False
    ) -> dict[str, Any]:
        """Return breeze-mode decision data.

        Args:
            strict: When ``True``, raise on failure.  Default ``False``.
        """
        return await self._get(ENDPOINT_DECISION_BREEZE, strict=strict)

    async def async_get_all(self, *, strict: bool = False) -> WavesData:
        """Fetch all six endpoints concurrently and return an aggregate model.

        :meth:`async_get_constellation` always uses strict semantics and acts
        as a connectivity probe.  The remaining five endpoints inherit *strict*.

        Args:
            strict: Applied to the non-constellation endpoint calls.

        Returns:
            :class:`~.models.WavesData` with all six payloads.

        Raises:
            RensonWavesCannotConnect: Device is unreachable (constellation).
            RensonWavesRequestError: Non-2xx or network error when
                ``strict=True``.
            RensonWavesResponseError: Invalid JSON when ``strict=True``.
        """
        (
            constellation,
            wifi_status,
            uptime,
            decision_room,
            decision_silent,
            decision_breeze,
        ) = await asyncio.gather(
            self.async_get_constellation(),
            self.async_get_wifi_status(strict=strict),
            self.async_get_global_uptime(strict=strict),
            self.async_get_decision_room(strict=strict),
            self.async_get_decision_silent(strict=strict),
            self.async_get_decision_breeze(strict=strict),
        )
        return WavesData(
            constellation=constellation,
            wifi_status=wifi_status,
            uptime=uptime,
            decision_room=decision_room,
            decision_silent=decision_silent,
            decision_breeze=decision_breeze,
        )
