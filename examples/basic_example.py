"""Basic example of using renson-waves-client."""

import asyncio

from renson_waves_client import RensonWavesCannotConnect, RensonWavesClient


async def main() -> None:
    client = RensonWavesClient(host="192.168.1.100")
    try:
        # Probe connectivity and read constellation
        constellation = await client.async_get_constellation()
        serial = constellation["global"]["serial"]["value"]
        name = constellation["global"]["device_name"]["value"]
        print(f"Connected to {name} (serial: {serial})")

        # Individual endpoints (non-strict — return {} on failure)
        wifi = await client.async_get_wifi_status()
        print(f"WiFi SSID : {wifi.get('global', {}).get('ssid', {}).get('value')}")

        uptime = await client.async_get_global_uptime()
        print(f"Uptime    : {uptime.get('global', {}).get('uptime', {}).get('value')} s")

    except RensonWavesCannotConnect:
        print("Device unreachable")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
