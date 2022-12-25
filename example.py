"""Sample script to use the Python API client for the Elmax Cloud service."""
import asyncio
import pprint

from elmax import Elmax

USERNAME = "username"
PASSWORD = "password"
PIN = "000000"
CONTROL_PANEL = "7e67sadfe35fgsdfg445d68b4fd4105d1be44d"


async def main():
    """The main part of the example script."""

    client = Elmax(username=USERNAME, password=PASSWORD)
    await client.connect()
    print("Is authenticated?", client.authorized)

    control_panels = await client.list_control_panels()

    print("Available control panels:")
    pprint.pprint(client.control_panels)

    print()
    # Get all available control panels
    print("Show all available control panels")
    print("---------------------------------")

    control_panels = {}
    for control_panel in control_panels:
        if control_panel["online"]:
            print("Device online?", bool(control_panel["online"]))
            print("Device ID:    ", control_panel["hash"])
            print("Device name:  ", control_panel["name"])
            print()

    print()

    # Limit to one control panel
    print("Show availables endpoints of one control panel:")
    control_panel = CONTROL_PANEL
    print("Control panel:", control_panel)
    units = await client.get_endpoints(control_panel, PIN)

    print("Zones:")
    pprint.pprint(client.zones)
    print("Outputs:")
    pprint.pprint(client.outputs)
    print("Areas:")
    pprint.pprint(client.areas)

    print()
    # Get the state of single endpoints
    print("Show the state of a given endpoint:")
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
