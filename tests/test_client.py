"""Tests for RensonWavesClient."""

from __future__ import annotations

from typing import Any

import aiohttp
import pytest
from aioresponses import aioresponses as aioresponses_mock

from renson_waves_client import (
    RensonWavesCannotConnect,
    RensonWavesClient,
    RensonWavesRequestError,
    RensonWavesResponseError,
    WavesData,
)

from .conftest import (
    BASE_URL,
    CONSTELLATION_PAYLOAD,
    DECISION_BREEZE_PAYLOAD,
    DECISION_ROOM_PAYLOAD,
    DECISION_SILENT_PAYLOAD,
    TEST_HOST,
    TEST_PORT,
    UPTIME_PAYLOAD,
    WIFI_STATUS_PAYLOAD,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

URLS: dict[str, str] = {
    "constellation": f"{BASE_URL}/constellation",
    "wifi_status": f"{BASE_URL}/wifi/client/status",
    "uptime": f"{BASE_URL}/global/uptime",
    "decision_room": f"{BASE_URL}/decision/room",
    "decision_silent": f"{BASE_URL}/decision/silent",
    "decision_breeze": f"{BASE_URL}/decision/breeze",
}


def _register_all(m: aioresponses_mock) -> None:
    """Register all six endpoints with their default payloads."""
    m.get(URLS["constellation"], payload=CONSTELLATION_PAYLOAD)
    m.get(URLS["wifi_status"], payload=WIFI_STATUS_PAYLOAD)
    m.get(URLS["uptime"], payload=UPTIME_PAYLOAD)
    m.get(URLS["decision_room"], payload=DECISION_ROOM_PAYLOAD)
    m.get(URLS["decision_silent"], payload=DECISION_SILENT_PAYLOAD)
    m.get(URLS["decision_breeze"], payload=DECISION_BREEZE_PAYLOAD)


# ---------------------------------------------------------------------------
# async_get_constellation – success, errors
# ---------------------------------------------------------------------------


async def test_constellation_success(client: RensonWavesClient) -> None:
    with aioresponses_mock() as m:
        m.get(URLS["constellation"], payload=CONSTELLATION_PAYLOAD)
        result = await client.async_get_constellation()

    assert result == CONSTELLATION_PAYLOAD
    assert result["global"]["serial"]["value"] == "RW-ABC1234567"
    assert result["global"]["device_name"]["value"] == "Renson WAVES"
    # sensor map
    sensor = result["sensor"]["s1"]
    assert sensor["type"] == "BathRoom"
    assert sensor["parameter"]["temp"]["value"] == 21.5
    assert sensor["parameter"]["rh"]["unit"] == "%"


async def test_constellation_cannot_connect(client: RensonWavesClient) -> None:
    with aioresponses_mock() as m:
        m.get(URLS["constellation"], exception=aiohttp.ClientConnectionError("refused"))
        with pytest.raises(RensonWavesCannotConnect):
            await client.async_get_constellation()


async def test_constellation_timeout(client: RensonWavesClient) -> None:
    with aioresponses_mock() as m:
        m.get(URLS["constellation"], exception=TimeoutError())
        with pytest.raises(RensonWavesCannotConnect):
            await client.async_get_constellation()


async def test_constellation_non_2xx(client: RensonWavesClient) -> None:
    with aioresponses_mock() as m:
        m.get(URLS["constellation"], status=503)
        with pytest.raises(RensonWavesRequestError):
            await client.async_get_constellation()


async def test_constellation_invalid_json(client: RensonWavesClient) -> None:
    with aioresponses_mock() as m:
        m.get(
            URLS["constellation"],
            body=b"<not json>",
            content_type="application/json",
        )
        with pytest.raises(RensonWavesResponseError):
            await client.async_get_constellation()


# ---------------------------------------------------------------------------
# Non-strict endpoints — default behaviour (strict=False)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "method_name, url_key, payload",
    [
        ("async_get_wifi_status", "wifi_status", WIFI_STATUS_PAYLOAD),
        ("async_get_global_uptime", "uptime", UPTIME_PAYLOAD),
        ("async_get_decision_room", "decision_room", DECISION_ROOM_PAYLOAD),
        ("async_get_decision_silent", "decision_silent", DECISION_SILENT_PAYLOAD),
        ("async_get_decision_breeze", "decision_breeze", DECISION_BREEZE_PAYLOAD),
    ],
)
async def test_endpoint_success(
    client: RensonWavesClient,
    method_name: str,
    url_key: str,
    payload: dict[str, Any],
) -> None:
    with aioresponses_mock() as m:
        m.get(URLS[url_key], payload=payload)
        result = await getattr(client, method_name)()
    assert result == payload


@pytest.mark.parametrize(
    "method_name, url_key",
    [
        ("async_get_wifi_status", "wifi_status"),
        ("async_get_global_uptime", "uptime"),
        ("async_get_decision_room", "decision_room"),
        ("async_get_decision_silent", "decision_silent"),
        ("async_get_decision_breeze", "decision_breeze"),
    ],
)
async def test_endpoint_non_2xx_non_strict_returns_empty(
    client: RensonWavesClient,
    method_name: str,
    url_key: str,
) -> None:
    with aioresponses_mock() as m:
        m.get(URLS[url_key], status=500)
        result = await getattr(client, method_name)()
    assert result == {}


@pytest.mark.parametrize(
    "method_name, url_key",
    [
        ("async_get_wifi_status", "wifi_status"),
        ("async_get_global_uptime", "uptime"),
        ("async_get_decision_room", "decision_room"),
        ("async_get_decision_silent", "decision_silent"),
        ("async_get_decision_breeze", "decision_breeze"),
    ],
)
async def test_endpoint_timeout_non_strict_returns_empty(
    client: RensonWavesClient,
    method_name: str,
    url_key: str,
) -> None:
    with aioresponses_mock() as m:
        m.get(URLS[url_key], exception=TimeoutError())
        result = await getattr(client, method_name)()
    assert result == {}


@pytest.mark.parametrize(
    "method_name, url_key",
    [
        ("async_get_wifi_status", "wifi_status"),
        ("async_get_global_uptime", "uptime"),
        ("async_get_decision_room", "decision_room"),
        ("async_get_decision_silent", "decision_silent"),
        ("async_get_decision_breeze", "decision_breeze"),
    ],
)
async def test_endpoint_invalid_json_non_strict_returns_empty(
    client: RensonWavesClient,
    method_name: str,
    url_key: str,
) -> None:
    with aioresponses_mock() as m:
        m.get(URLS[url_key], body=b"bad json{{", content_type="application/json")
        result = await getattr(client, method_name)()
    assert result == {}


# ---------------------------------------------------------------------------
# Non-strict endpoints — strict=True behaviour
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "method_name, url_key",
    [
        ("async_get_wifi_status", "wifi_status"),
        ("async_get_global_uptime", "uptime"),
        ("async_get_decision_room", "decision_room"),
        ("async_get_decision_silent", "decision_silent"),
        ("async_get_decision_breeze", "decision_breeze"),
    ],
)
async def test_endpoint_non_2xx_strict_raises(
    client: RensonWavesClient,
    method_name: str,
    url_key: str,
) -> None:
    with aioresponses_mock() as m:
        m.get(URLS[url_key], status=404)
        with pytest.raises(RensonWavesRequestError):
            await getattr(client, method_name)(strict=True)


@pytest.mark.parametrize(
    "method_name, url_key",
    [
        ("async_get_wifi_status", "wifi_status"),
        ("async_get_global_uptime", "uptime"),
        ("async_get_decision_room", "decision_room"),
        ("async_get_decision_silent", "decision_silent"),
        ("async_get_decision_breeze", "decision_breeze"),
    ],
)
async def test_endpoint_timeout_strict_raises(
    client: RensonWavesClient,
    method_name: str,
    url_key: str,
) -> None:
    with aioresponses_mock() as m:
        m.get(URLS[url_key], exception=TimeoutError())
        with pytest.raises(RensonWavesRequestError):
            await getattr(client, method_name)(strict=True)


@pytest.mark.parametrize(
    "method_name, url_key",
    [
        ("async_get_wifi_status", "wifi_status"),
        ("async_get_global_uptime", "uptime"),
        ("async_get_decision_room", "decision_room"),
        ("async_get_decision_silent", "decision_silent"),
        ("async_get_decision_breeze", "decision_breeze"),
    ],
)
async def test_endpoint_invalid_json_strict_raises(
    client: RensonWavesClient,
    method_name: str,
    url_key: str,
) -> None:
    with aioresponses_mock() as m:
        m.get(URLS[url_key], body=b"bad json{{", content_type="application/json")
        with pytest.raises(RensonWavesResponseError):
            await getattr(client, method_name)(strict=True)


# ---------------------------------------------------------------------------
# async_get_all – concurrent aggregate fetch
# ---------------------------------------------------------------------------


async def test_get_all_success(client: RensonWavesClient) -> None:
    with aioresponses_mock() as m:
        _register_all(m)
        data = await client.async_get_all()

    assert isinstance(data, WavesData)
    assert data.constellation == CONSTELLATION_PAYLOAD
    assert data.wifi_status == WIFI_STATUS_PAYLOAD
    assert data.uptime == UPTIME_PAYLOAD
    assert data.decision_room == DECISION_ROOM_PAYLOAD
    assert data.decision_silent == DECISION_SILENT_PAYLOAD
    assert data.decision_breeze == DECISION_BREEZE_PAYLOAD

    # Verify convenient nested access
    assert data.constellation["global"]["serial"]["value"] == "RW-ABC1234567"
    assert data.wifi_status["global"]["ssid"]["value"] == "HomeNetwork"
    assert data.uptime["global"]["uptime"]["value"] == 407949
    assert data.decision_room["global"]["decision"]["value"] == 50.0
    assert data.decision_silent["global"]["reduction"]["value"] == 30
    assert data.decision_breeze["global"]["temperature"]["value"] == 22.0


async def test_get_all_non_constellation_failures_return_empty_by_default(
    client: RensonWavesClient,
) -> None:
    """When non-constellation endpoints fail, async_get_all returns empty dicts."""
    with aioresponses_mock() as m:
        m.get(URLS["constellation"], payload=CONSTELLATION_PAYLOAD)
        m.get(URLS["wifi_status"], status=503)
        m.get(URLS["uptime"], exception=TimeoutError())
        m.get(URLS["decision_room"], body=b"bad", content_type="application/json")
        m.get(URLS["decision_silent"], status=404)
        m.get(URLS["decision_breeze"], exception=aiohttp.ClientConnectionError())
        data = await client.async_get_all()

    assert data.constellation == CONSTELLATION_PAYLOAD
    assert data.wifi_status == {}
    assert data.uptime == {}
    assert data.decision_room == {}
    assert data.decision_silent == {}
    assert data.decision_breeze == {}


async def test_get_all_constellation_failure_raises(
    client: RensonWavesClient,
) -> None:
    with aioresponses_mock() as m:
        m.get(URLS["constellation"], exception=aiohttp.ClientConnectionError("down"))
        # other endpoints should not be called if constellation raises first, but
        # asyncio.gather fires them all concurrently — just register them to avoid
        # ConnectionRefusedError noise from aioresponses passthrough
        m.get(URLS["wifi_status"], payload=WIFI_STATUS_PAYLOAD)
        m.get(URLS["uptime"], payload=UPTIME_PAYLOAD)
        m.get(URLS["decision_room"], payload=DECISION_ROOM_PAYLOAD)
        m.get(URLS["decision_silent"], payload=DECISION_SILENT_PAYLOAD)
        m.get(URLS["decision_breeze"], payload=DECISION_BREEZE_PAYLOAD)
        with pytest.raises(RensonWavesCannotConnect):
            await client.async_get_all()


# ---------------------------------------------------------------------------
# Session management & context manager
# ---------------------------------------------------------------------------


async def test_context_manager_closes_internal_session() -> None:
    async with RensonWavesClient(host=TEST_HOST, port=TEST_PORT) as c:
        with aioresponses_mock() as m:
            m.get(URLS["constellation"], payload=CONSTELLATION_PAYLOAD)
            await c.async_get_constellation()
    # After exit the session should be None / closed
    assert c._session is None or c._session.closed


async def test_external_session_not_closed_by_client() -> None:
    ext_session = aiohttp.ClientSession()
    try:
        client = RensonWavesClient(host=TEST_HOST, port=TEST_PORT, session=ext_session)
        with aioresponses_mock() as m:
            m.get(URLS["constellation"], payload=CONSTELLATION_PAYLOAD)
            await client.async_get_constellation()
        await client.close()  # must NOT close the external session
        assert not ext_session.closed
    finally:
        await ext_session.close()


async def test_close_is_idempotent() -> None:
    client = RensonWavesClient(host=TEST_HOST, port=TEST_PORT)
    with aioresponses_mock() as m:
        m.get(URLS["constellation"], payload=CONSTELLATION_PAYLOAD)
        await client.async_get_constellation()
    await client.close()
    await client.close()  # must not raise


# ---------------------------------------------------------------------------
# Payload field spot-checks
# ---------------------------------------------------------------------------


async def test_wifi_status_fields(client: RensonWavesClient) -> None:
    with aioresponses_mock() as m:
        m.get(URLS["wifi_status"], payload=WIFI_STATUS_PAYLOAD)
        result = await client.async_get_wifi_status()

    g = result["global"]
    assert g["ssid"]["value"] == "HomeNetwork"
    assert g["connection_status"]["value"] == "connected"


async def test_uptime_field(client: RensonWavesClient) -> None:
    with aioresponses_mock() as m:
        m.get(URLS["uptime"], payload=UPTIME_PAYLOAD)
        result = await client.async_get_global_uptime()

    assert result["global"]["uptime"]["value"] == 407949


async def test_decision_room_fields(client: RensonWavesClient) -> None:
    with aioresponses_mock() as m:
        m.get(URLS["decision_room"], payload=DECISION_ROOM_PAYLOAD)
        result = await client.async_get_decision_room()

    assert result["global"]["decision"]["value"] == 50.0
    assert result["global"]["level"]["value"] == 2


async def test_decision_silent_fields(client: RensonWavesClient) -> None:
    with aioresponses_mock() as m:
        m.get(URLS["decision_silent"], payload=DECISION_SILENT_PAYLOAD)
        result = await client.async_get_decision_silent()

    assert result["global"]["decision"]["value"] is True
    assert result["global"]["reduction"]["value"] == 30


async def test_decision_breeze_fields(client: RensonWavesClient) -> None:
    with aioresponses_mock() as m:
        m.get(URLS["decision_breeze"], payload=DECISION_BREEZE_PAYLOAD)
        result = await client.async_get_decision_breeze()

    assert result["global"]["decision"]["value"] is True
    assert result["global"]["temperature"]["value"] == 22.0


async def test_constellation_sensor_map(client: RensonWavesClient) -> None:
    with aioresponses_mock() as m:
        m.get(URLS["constellation"], payload=CONSTELLATION_PAYLOAD)
        result = await client.async_get_constellation()

    sensors = result["sensor"]
    assert "s1" in sensors
    assert "s2" in sensors
    params = sensors["s1"]["parameter"]
    assert params["avoc"]["value"] == 120
    assert params["press"]["unit"] == "hPa"
    assert params["rssi"]["value"] == -68


# ---------------------------------------------------------------------------
# Base URL construction
# ---------------------------------------------------------------------------


async def test_custom_port_in_base_url() -> None:
    c = RensonWavesClient(host="10.0.0.1", port=9090)
    assert c._base_url == "http://10.0.0.1:9090/v1"
    await c.close()


async def test_default_port_in_base_url() -> None:
    c = RensonWavesClient(host="10.0.0.1")
    assert c._base_url == "http://10.0.0.1:8000/v1"
    await c.close()
