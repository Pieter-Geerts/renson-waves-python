"""Example using async context manager — session is closed automatically."""

import asyncio

from renson_waves_client import RensonWavesCannotConnect, RensonWavesClient


async def main() -> None:
    async with RensonWavesClient(host="192.168.1.100") as client:
        try:
            data = await client.async_get_all()
        except RensonWavesCannotConnect:
            print("Device unreachable")
            return

    name = data.constellation.get("global", {}).get("device_name", {}).get("value", "Renson WAVES")
    ssid = data.wifi_status.get("global", {}).get("ssid", {}).get("value")
    uptime = data.uptime.get("global", {}).get("uptime", {}).get("value")
    print(f"{name} | WiFi: {ssid} | Uptime: {uptime} s")


if __name__ == "__main__":
    asyncio.run(main())
