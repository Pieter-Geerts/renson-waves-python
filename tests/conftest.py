"""Pytest configuration and shared fixtures for renson-waves-client tests."""

from __future__ import annotations

from typing import Any

import pytest_asyncio

from renson_waves_client import RensonWavesClient

# ---------------------------------------------------------------------------
# Test targets
# ---------------------------------------------------------------------------

TEST_HOST = "192.168.1.100"
TEST_PORT = 8000
BASE_URL = f"http://{TEST_HOST}:{TEST_PORT}/v1"

# ---------------------------------------------------------------------------
# Realistic payload fixtures
# ---------------------------------------------------------------------------

CONSTELLATION_PAYLOAD: dict[str, Any] = {
    "global": {
        "serial": {"value": "RW-ABC1234567"},
        "device_name": {"value": "Renson WAVES"},
        "firmware_version": {"value": "1.2.3"},
    },
    "sensor": {
        "s1": {
            "type": "BathRoom",
            "parameter": {
                "temp": {"value": 21.5, "unit": "°C"},
                "rh": {"value": 65.0, "unit": "%"},
                "ah": {"value": 10.2, "unit": "g/m³"},
                "avoc": {"value": 120, "unit": "ppb"},
                "press": {"value": 1013.25, "unit": "hPa"},
                "rssi": {"value": -68, "unit": "dBm"},
            },
        },
        "s2": {
            "type": "LivingRoom",
            "parameter": {
                "temp": {"value": 20.0, "unit": "°C"},
                "rh": {"value": 50.0, "unit": "%"},
                "ah": {"value": 8.7, "unit": "g/m³"},
                "avoc": {"value": 95, "unit": "ppb"},
                "press": {"value": 1013.10, "unit": "hPa"},
                "rssi": {"value": -72, "unit": "dBm"},
            },
        },
    },
}

WIFI_STATUS_PAYLOAD: dict[str, Any] = {
    "global": {
        "ssid": {"value": "HomeNetwork"},
        "connection_status": {"value": "connected"},
        "ip": {"value": "192.168.1.100"},
        "mac": {"value": "4c:eb:d6:60:3a:dc"},
        "rssi": {"value": -55},
    }
}

UPTIME_PAYLOAD: dict[str, Any] = {
    "global": {
        "uptime": {"value": 407949},
    }
}

DECISION_ROOM_PAYLOAD: dict[str, Any] = {
    "global": {
        "decision": {"value": 50.0},
        "level": {"value": 2},
    }
}

DECISION_SILENT_PAYLOAD: dict[str, Any] = {
    "global": {
        "decision": {"value": True},
        "reduction": {"value": 30},
    }
}

DECISION_BREEZE_PAYLOAD: dict[str, Any] = {
    "global": {
        "decision": {"value": True},
        "temperature": {"value": 22.0},
    }
}

# ---------------------------------------------------------------------------
# Client fixture
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def client() -> RensonWavesClient:
    """Return a :class:`RensonWavesClient` connected to the test host."""
    async with RensonWavesClient(host=TEST_HOST, port=TEST_PORT) as c:
        yield c  # type: ignore[misc]
