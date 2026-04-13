"""Typed data models for renson-waves-client."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class WavesData:
    """Aggregate data model combining all six WAVES API endpoints.

    Each field holds the raw JSON payload returned by the corresponding
    endpoint, preserved as a plain :class:`dict` for forward-compatibility.
    Fields for unreachable endpoints (non-strict mode) are empty dicts.

    Example::

        data = await client.async_get_all()
        serial = data.constellation.get("global", {}).get("serial", {}).get("value")
        ssid   = data.wifi_status.get("global", {}).get("ssid", {}).get("value")
    """

    constellation: dict[str, Any]
    wifi_status: dict[str, Any]
    uptime: dict[str, Any]
    decision_room: dict[str, Any]
    decision_silent: dict[str, Any]
    decision_breeze: dict[str, Any]
