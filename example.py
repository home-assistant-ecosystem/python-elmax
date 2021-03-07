"""Sample script to use the Python API client for the Elmax Cloud service."""
import asyncio
import pprint

from elmax import Elmax

USERNAME = "username"
PASSWORD = "password"
PIN = "12345678"


async def main():
    """The main part of the example script."""

    client = Elmax(username=USERNAME, password=PASSWORD)
    await client.connect()
    print("Is authenticated?", client.authorized)

    devices = await client.list_devices()

    print("Available devices:")
    pprint.pprint(devices)

    print()
    # Get all units
    units = {}
    for unit in devices:
        if unit["online"]:
            print("Device online?", bool(unit["online"]))
            print("Device ID:", unit["hash"])
            print("Availables units:")
            units = await client.get_units(unit["hash"], PIN)

    print("Zones:")
    pprint.pprint(client.zones)
    print("Outputs:")
    pprint.pprint(client.outputs)
    print("Areas:")
    pprint.pprint(client.areas)

    print()
    # Get the state of an entity
    entity = client.zones[2]
    print("Entity:", entity["nome"])
    state = await client.get_status(entity["endpointId"])
    print("State?", state["esclusa"])
    entity = client.zones[5]
    print("Entity:", entity["nome"])
    state = await client.get_status(entity["endpointId"])
    print("State?", state["esclusa"])


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
