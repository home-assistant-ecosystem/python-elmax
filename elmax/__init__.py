"""Client for the Elmax Cloud service."""
from yarl import URL
import asyncio
import logging
import httpx
import json

from .constants import (
    BASE_URL,
    ENDPOINT_DEVICES,
    ENDPOINT_LOGIN,
    ENDPOINT_STATUS_ENTITY_ID,
    ENDPOINT_ENTITY_ID_COMMAND,
    ENDPOINT_DISCOVERY,
    USER_AGENT,
    ZONE,
    OUTPUT,
    AREA,
)

headers = {
    "user-agent": USER_AGENT,
    "Accept": "application/json, text/plain, */*",
}

_LOGGER = logging.getLogger(__name__)


class Elmax(object):
    """A class for handling the data retrieval."""

    def __init__(
        self,
        username: str = None,
        password: str = None,
        device_id: str = None,
    ):
        """Initialize the connection."""
        self.username = username
        self.password = password
        self.devices = None
        self.authorized = False
        self.authorization = None
        self.areas = self.outputs = self.zones = {}

        self.registry = DeviceRegistry()

    async def connect(self):
        """Establish connection to the API."""
        url = URL(BASE_URL) / ENDPOINT_LOGIN
        data = {
            "username": self.username,
            "password": self.password,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(str(url), headers=headers, data=data)

        _LOGGER.debug("Status code:", response.status_code)

        try:
            response_data = response.json()
            self.authorization = response_data["token"]
            self.authorized = True
        # The API doesn't respond with 401 but there will be no JSON
        except json.decoder.JSONDecodeError:
            self.authorized = False
            _LOGGER.error("Credentials are not valid")

    async def disconnect(self):
        """Terminate the connection to the API."""
        if self.authorized:
            self.authorized = False

    async def get_devices(self):
        """Retrieve the devices."""
        if self.authorized is False:
            self.connect()

        url = URL(BASE_URL) / ENDPOINT_DEVICES
        headers["Authorization"] = self.authorization

        async with httpx.AsyncClient() as client:
            response = await client.get(str(url), headers=headers)

        _LOGGER.debug("Status code:", response.status_code)

        for response_entry in response.json():
            device = AvailableDevice.create_new_device(response_entry)
            self.registry.register(device)

    async def list_devices(self):
        """List all available devices."""
        await self.get_devices()

        device_list = []
        for device in self.registry.devices():
            device_list.append(
                {"online": device.online, "hash": device.hash, "name": device.name}
            )

        return device_list

    async def get_units(self, device_id, pin):
        """List all units of a devices."""
        if self.authorized is False:
            self.connect()

        url = URL(BASE_URL) / ENDPOINT_DISCOVERY / device_id / str(pin)

        headers["Authorization"] = self.authorization

        async with httpx.AsyncClient() as client:
            response = await client.get(str(url), headers=headers)

        response_data = response.json()

        if response_data[ZONE]:
            self.zones = response_data[ZONE]
        if response_data[OUTPUT]:
            self.outputs = response_data[OUTPUT]
        if response_data[AREA]:
            self.areas = response_data[AREA]

    async def get_status(self, entity_id):
        """Get the status of an unit."""
        if self.authorized is False:
            self.connect()

        url = URL(BASE_URL) / ENDPOINT_STATUS_ENTITY_ID / entity_id

        headers["Authorization"] = self.authorization

        async with httpx.AsyncClient() as client:
            response = await client.get(str(url), headers=headers)

        return response.json()["zone"][0]


class AvailableDevice:
    """Representation of an available device."""

    def __init__(self, hash, online, name):
        """Initialize the new device."""
        self.hash = hash
        self.online = online
        self.name = name

    @staticmethod
    def create_new_device(response_entry):
        """Create a new device."""
        device = AvailableDevice(
            hash=response_entry["hash"],
            online=bool(response_entry["centrale_online"]),
            name=response_entry["username"][0]["label"],
        )
        return device


class DeviceRegistry(object):
    """Representation of the devices registry."""

    def __init__(self):
        """Initialize the device registry."""
        self.devices_by_hash = {}

    def register(self, device):
        """Register a new device."""
        self.devices_by_hash[device.hash] = device

    def devices(self) -> list:
        """Get all available devices."""
        return list(self.devices_by_hash.values())
