"""Advanced example: error handling, retry logic, periodic monitoring."""

import asyncio

from renson_waves_client import (
    RensonWavesCannotConnect,
    RensonWavesClient,
    RensonWavesError,
)


async def get_all_with_retry(host: str, max_retries: int = 3) -> dict:  # type: ignore[type-arg]
    """Fetch all device data with exponential-backoff retry."""
    for attempt in range(max_retries):
        try:
            async with RensonWavesClient(host=host) as client:
                data = await client.async_get_all()
                return {
                    "serial": data.constellation.get("global", {}).get("serial", {}).get("value"),
                    "ssid": data.wifi_status.get("global", {}).get("ssid", {}).get("value"),
                    "uptime": data.uptime.get("global", {}).get("uptime", {}).get("value"),
                    "room_decision": data.decision_room.get("global", {}).get("decision", {}).get("value"),
                }
        except RensonWavesCannotConnect as exc:
            if attempt < max_retries - 1:
                wait = 2**attempt
                print(f"Attempt {attempt + 1} failed ({exc}), retrying in {wait}s...")
                await asyncio.sleep(wait)
            else:
                raise
    return {}


async def monitor(host: str, interval: int = 30) -> None:
    """Poll the device every *interval* seconds."""
    async with RensonWavesClient(host=host) as client:
        while True:
            try:
                data = await client.async_get_all()
                uptime = data.uptime.get("global", {}).get("uptime", {}).get("value")
                ssid = data.wifi_status.get("global", {}).get("ssid", {}).get("value")
                room = data.decision_room.get("global", {}).get("decision", {}).get("value")

                # Sensor values from constellation
                sensors = data.constellation.get("sensor", {})
                for sid, sensor in sensors.items():
                    params = sensor.get("parameter", {})
                    temp = params.get("temp", {}).get("value")
                    rh = params.get("rh", {}).get("value")
                    print(f"[{uptime}s] WiFi:{ssid} room_decision:{room} "
                          f"sensor {sid}: {temp}°C / {rh}%")

            except RensonWavesError as exc:
                print(f"Error: {exc}")

            await asyncio.sleep(interval)


async def main() -> None:
    host = "192.168.1.100"

    print("=== Fetch all with retry ===")
    try:
        status = await get_all_with_retry(host)
        print(status)
    except RensonWavesCannotConnect:
        print("Device unreachable after retries")

    print("\n=== Periodic monitor (3 polls) ===")
    # Runs forever in production; here we cancel after a few polls for demo.
    task = asyncio.create_task(monitor(host, interval=5))
    await asyncio.sleep(12)
    task.cancel()


if __name__ == "__main__":
    asyncio.run(main())
