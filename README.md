# renson-waves-client

[![PyPI](https://img.shields.io/pypi/v/renson-waves-client)](https://pypi.org/project/renson-waves-client/)
[![Python](https://img.shields.io/pypi/pyversions/renson-waves-client)](https://pypi.org/project/renson-waves-client/)
[![CI](https://github.com/Pietergeerts/renson-waves-python/actions/workflows/ci.yml/badge.svg)](https://github.com/Pietergeerts/renson-waves-python/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Async Python 3.12+ client for the **Renson WAVES** local HTTP API (`/v1`).

---

## Purpose & Scope

This library provides a thin, typed async wrapper around the Renson WAVES device's local REST API.
It is intentionally **free of Home Assistant imports** so that it can be used as a standalone
dependency from any async Python application — including Home Assistant custom or core integrations.

What it does:

- Probes connectivity via `GET /v1/constellation`
- Fetches six data endpoints individually or concurrently
- Exposes clean custom exceptions for all failure scenarios
- Ships with a `py.typed` marker for downstream type checking

What it does **not** do:

- No Home Assistant helpers, `config_entries`, entity registration, etc.
- No parsing / mapping of raw payloads — raw `dict` is returned for forward compatibility

---

## Installation

```bash
pip install renson-waves-client
```

Requires Python ≥ 3.12 and `aiohttp` ≥ 3.9.

---

## Quick-start

### Create a client

```python
from renson_waves_client import RensonWavesClient

# uses default port 8000
client = RensonWavesClient("192.168.1.100")

# explicit port
client = RensonWavesClient("192.168.1.100", port=8000)

# bring your own aiohttp session (e.g. from Home Assistant)
import aiohttp
session = aiohttp.ClientSession()
client = RensonWavesClient("192.168.1.100", session=session)
```

### Probe connectivity

```python
from renson_waves_client import RensonWavesCannotConnect

try:
    constellation = await client.async_get_constellation()
except RensonWavesCannotConnect:
    print("device unreachable")
```

### Fetch individual endpoints

```python
# always returns a dict (empty on failure unless strict=True)
wifi   = await client.async_get_wifi_status()
uptime = await client.async_get_global_uptime()
room   = await client.async_get_decision_room()
silent = await client.async_get_decision_silent()
breeze = await client.async_get_decision_breeze()

# access nested values
ssid = wifi.get("global", {}).get("ssid", {}).get("value")
```

### Fetch all data concurrently

```python
from renson_waves_client import WavesData

data: WavesData = await client.async_get_all()

serial      = data.constellation["global"]["serial"]["value"]
device_name = data.constellation["global"]["device_name"]["value"]
ssid        = data.wifi_status["global"]["ssid"]["value"]
uptime_secs = data.uptime["global"]["uptime"]["value"]
room_level  = data.decision_room["global"]["level"]["value"]
```

### Async context manager (recommended)

```python
async with RensonWavesClient("192.168.1.100") as client:
    data = await client.async_get_all()
# session is closed automatically
```

### Manual close

```python
client = RensonWavesClient("192.168.1.100")
try:
    data = await client.async_get_all()
finally:
    await client.close()
```

---

## Exception reference

| Exception                  | When raised                                                              |
| -------------------------- | ------------------------------------------------------------------------ |
| `RensonWavesError`         | Base class for all library exceptions                                    |
| `RensonWavesCannotConnect` | Network / connection failure during `async_get_constellation`            |
| `RensonWavesRequestError`  | Non-2xx HTTP response (strict mode) or network error (strict, non-probe) |
| `RensonWavesResponseError` | Response body is not valid JSON (strict mode)                            |

```python
from renson_waves_client import (
    RensonWavesError,
    RensonWavesCannotConnect,
    RensonWavesRequestError,
    RensonWavesResponseError,
)

try:
    data = await client.async_get_all()
except RensonWavesCannotConnect:
    # device is unreachable — retry or surface config error
    ...
except RensonWavesError:
    # any other library error
    ...
```

---

## Strict mode

The five non-probe endpoint methods (`async_get_wifi_status`, `async_get_global_uptime`,
`async_get_decision_room`, `async_get_decision_silent`, `async_get_decision_breeze`) and
`async_get_all` accept a keyword argument `strict: bool = False`.

| `strict`          | On failure                                                                      |
| ----------------- | ------------------------------------------------------------------------------- |
| `False` (default) | Returns `{}` — mirrors the behaviour of the current Renson WAVES HA integration |
| `True`            | Raises the appropriate exception                                                |

```python
# lenient (default) — safe for polling coordinators
wifi = await client.async_get_wifi_status()          # {} on failure

# strict — useful when you need the value or want to surface errors explicitly
wifi = await client.async_get_wifi_status(strict=True)  # raises on failure
```

---

## Known payload fields

```
constellation.global.serial.value          → device serial number
constellation.global.device_name.value     → human-readable device name
constellation.global.firmware_version.value

wifi_status.global.ssid.value
wifi_status.global.connection_status.value
wifi_status.global.ip.value
wifi_status.global.mac.value
wifi_status.global.rssi.value

uptime.global.uptime.value                 → uptime in seconds

decision_room.global.decision.value
decision_room.global.level.value

decision_silent.global.decision.value
decision_silent.global.reduction.value

decision_breeze.global.decision.value
decision_breeze.global.temperature.value

# Sensor map (constellation)
constellation.sensor.<id>.type
constellation.sensor.<id>.parameter.<param>.value
constellation.sensor.<id>.parameter.<param>.unit
# known params: temp, rh, ah, avoc, press, rssi
```

---

## Home Assistant integration

This library is designed for use from an HA integration without coupling to it.

### Dependency

In your integration's `manifest.json`:

```json
{
  "requirements": ["renson-waves-client==0.1.0"]
}
```

### Config-flow pattern

```python
from renson_waves_client import RensonWavesClient, RensonWavesCannotConnect

class RensonWavesConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    async def async_step_user(self, user_input=None):
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input["host"]
            port = user_input.get("port", 8000)
            client = RensonWavesClient(
                host, port=port,
                session=async_get_clientsession(self.hass),
            )
            try:
                constellation = await client.async_get_constellation()
            except RensonWavesCannotConnect:
                errors["base"] = "cannot_connect"
            else:
                # Unique ID: prefer serial, fall back to host:port
                serial: str = (
                    constellation.get("global", {})
                    .get("serial", {})
                    .get("value") or f"{host}:{port}"
                )
                # Title: prefer device_name, fall back to generic
                title: str = (
                    constellation.get("global", {})
                    .get("device_name", {})
                    .get("value") or "Renson WAVES"
                )
                await self.async_set_unique_id(serial)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=title, data=user_input)

        return self.async_show_form(step_id="user", errors=errors)
```

### Coordinator pattern

```python
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from renson_waves_client import RensonWavesClient, WavesData, RensonWavesCannotConnect

class RensonWavesCoordinator(DataUpdateCoordinator[WavesData]):

    def __init__(self, hass, client: RensonWavesClient) -> None:
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=30))
        self.client = client

    async def _async_update_data(self) -> WavesData:
        try:
            return await self.client.async_get_all()
        except RensonWavesCannotConnect as err:
            raise UpdateFailed(f"Cannot connect: {err}") from err
```

---

## Development

```bash
# Create virtual environment
python3.12 -m venv .venv
source .venv/bin/activate

# Install with dev extras
pip install -e ".[dev]"

# Lint
ruff check src tests
ruff format src tests

# Type check
mypy src

# Tests with coverage
pytest

# Build distribution
python -m build
```

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## Usage

### Basic Example

```python
import asyncio
from renson_waves_python import RensonWaves

async def main():
    # Initialize the client
    client = RensonWaves(host="192.168.0.228", api_key="")

    # Get device uptime
    uptime = await client.async_get_uptime()
    print(f"Device uptime: {uptime}")

    # Get WiFi status
    wifi_status = await client.async_get_wifi_status()
    print(f"WiFi: {wifi_status.status}")

    # Get room decision data
    room_data = await client.async_get_room_decision()
    print(f"Room type: {room_data.type}")

    # Enable boost mode
    await client.async_set_room_boost(enable=True, level=200, timeout=900)

    # Get sensors
    sensors = await client.async_get_sensors()
    for sensor_id, sensor in sensors.items():
        print(f"Sensor {sensor_id}: {sensor.name} - {sensor.type}")

asyncio.run(main())
```

## Features

- Get device uptime and basic info
- Monitor WiFi connection status
- Get detailed room decision configuration
- Control boost mode
- Manage silent mode schedules
- Monitor environmental sensors
- Get Breeze feature configuration

## API Reference

See [API_REFERENCE.md](API_REFERENCE.md) for detailed endpoint documentation.

## License

MIT
