"""Tests for WavesData aggregate model."""

from __future__ import annotations

from typing import Any

from renson_waves_client import WavesData

from .conftest import (
    CONSTELLATION_PAYLOAD,
    DECISION_BREEZE_PAYLOAD,
    DECISION_ROOM_PAYLOAD,
    DECISION_SILENT_PAYLOAD,
    UPTIME_PAYLOAD,
    WIFI_STATUS_PAYLOAD,
)


def _make_data(**overrides: dict[str, Any]) -> WavesData:
    base: dict[str, Any] = {
        "constellation": CONSTELLATION_PAYLOAD,
        "wifi_status": WIFI_STATUS_PAYLOAD,
        "uptime": UPTIME_PAYLOAD,
        "decision_room": DECISION_ROOM_PAYLOAD,
        "decision_silent": DECISION_SILENT_PAYLOAD,
        "decision_breeze": DECISION_BREEZE_PAYLOAD,
    }
    base.update(overrides)
    return WavesData(**base)


def test_waves_data_creation() -> None:
    data = _make_data()
    assert data.constellation is CONSTELLATION_PAYLOAD
    assert data.wifi_status is WIFI_STATUS_PAYLOAD
    assert data.uptime is UPTIME_PAYLOAD
    assert data.decision_room is DECISION_ROOM_PAYLOAD
    assert data.decision_silent is DECISION_SILENT_PAYLOAD
    assert data.decision_breeze is DECISION_BREEZE_PAYLOAD


def test_waves_data_empty_fields_allowed() -> None:
    data = WavesData(
        constellation=CONSTELLATION_PAYLOAD,
        wifi_status={},
        uptime={},
        decision_room={},
        decision_silent={},
        decision_breeze={},
    )
    assert data.wifi_status == {}
    assert data.uptime == {}


def test_waves_data_ha_serial_extraction() -> None:
    """Demonstrate the HA unique-id extraction pattern."""
    data = _make_data()
    serial: str = (
        data.constellation.get("global", {}).get("serial", {}).get("value") or ""
    )
    assert serial == "RW-ABC1234567"


def test_waves_data_ha_device_name_extraction() -> None:
    """Demonstrate the HA title extraction pattern with fallback."""
    data = _make_data()
    title: str = (
        data.constellation.get("global", {}).get("device_name", {}).get("value")
        or "Renson WAVES"
    )
    assert title == "Renson WAVES"


def test_waves_data_ha_device_name_fallback() -> None:
    """When device_name is absent, the HA fallback title should be used."""
    data = WavesData(
        constellation={},
        wifi_status={},
        uptime={},
        decision_room={},
        decision_silent={},
        decision_breeze={},
    )
    title: str = (
        data.constellation.get("global", {}).get("device_name", {}).get("value")
        or "Renson WAVES"
    )
    assert title == "Renson WAVES"
