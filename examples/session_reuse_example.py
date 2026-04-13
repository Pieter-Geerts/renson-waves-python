"""Example reusing an aiohttp session (e.g. shared with Home Assistant)."""

import asyncio

import aiohttp

from renson_waves_client import RensonWavesClient


async def main() -> None:
    # Pass an external session — the client will NOT close it.
    async with aiohttp.ClientSession() as session:
        client = RensonWavesClient(host="192.168.1.100", session=session)

        constellation = await client.async_get_constellation()
        print("Serial:", constellation["global"]["serial"]["value"])

        wifi = await client.async_get_wifi_status()
        print("SSID  :", wifi.get("global", {}).get("ssid", {}).get("value"))

        # client.close() is a no-op here; session is owned by the caller


if __name__ == "__main__":
    asyncio.run(main())
