"""Client for the Elmax Cloud services."""
from yarl import URL
import logging
import httpx
import json

from . import exceptions

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
        control_panel_id: str = None,
    ):
        """Initialize the connection."""
        self.username = username
        self.password = password
        self.control_panel_id = control_panel_id
        self.authorized = False
        self.authorization = None
        self._areas = self._outputs = self._zones = []

        self.registry = DeviceRegistry()

    async def connect(self):
        """Establish connection to the API."""
        url = URL(BASE_URL) / ENDPOINT_LOGIN
        data = {
            "username": self.username,
            "password": self.password,
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(str(url), headers=headers, data=data)
                _LOGGER.debug("Status code:", response.status_code)
        except httpx.ConnectError:
            raise exceptions.ElmaxConnectionError(f"Connection to {BASE_URL} failed")

        try:
            response_data = response.json()
            self.authorization = response_data["token"]
            self.authorized = True
        # The API doesn't respond with 401 but there will be no JSON
        except (json.decoder.JSONDecodeError, TypeError, KeyError):
            self.authorized = False
            raise exceptions.ElmaxConnectionError("Credentials are not valid")

    async def disconnect(self):
        """Terminate the connection to the API."""
        if self.authorized:
            self.authorized = False

    @property
    def is_authenticated(self):
        """Get the state of the authentication."""
        return self.authorized

    @property
    def control_panels(self):
        """Get the control panels."""
        return self.list_control_panels()

    @property
    def endpoints(self):
        """Get the endpoints."""
        raise NotImplementedError

    @property
    def zones(self):
        """Get the zones."""
        return self._zones

    @property
    def outputs(self):
        """Get the outputs."""
        return self._outputs

    @property
    def areas(self):
        """Get the areas."""
        return self._areas

    async def get_control_panels(self):
        """Retrieve the present control panels."""
        if self.authorized is False:
            await self.connect()

        url = URL(BASE_URL) / ENDPOINT_DEVICES
        headers["Authorization"] = self.authorization

        async with httpx.AsyncClient() as client:
            response = await client.get(str(url), headers=headers)

        _LOGGER.debug("Status code:", response.status_code)

        for response_entry in response.json():
            control_panel = AvailableControlPanel.create_new_control_panel(
                response_entry
            )
            self.registry.register(control_panel)

    async def list_control_panels(self):
        """List all available control panels."""
        await self.get_control_panels()

        control_panels_list = []
        for control_panel in self.registry.devices():
            control_panels_list.append(
                {
                    "online": control_panel.online,
                    "hash": control_panel.hash,
                    "name": control_panel.name,
                }
            )

        return control_panels_list

    async def get_endpoints(self, control_panel_id, pin):
        """List all endpoints of a control panel."""
        if self.authorized is False:
            await self.connect()

        url = URL(BASE_URL) / ENDPOINT_DISCOVERY / control_panel_id / str(pin)

        headers["Authorization"] = self.authorization

        async with httpx.AsyncClient() as client:
            response = await client.get(str(url), headers=headers)

        response_data = response.json()

        if response_data[ZONE]:
            self._zones = response_data[ZONE]
        if response_data[OUTPUT]:
            self._outputs = response_data[OUTPUT]
        if response_data[AREA]:
            self._areas = response_data[AREA]

    async def get_status(self, endpoint_id):
        """Get the status of an endpoint."""
        if self.authorized is False:
            self.connect()

        url = URL(BASE_URL) / ENDPOINT_STATUS_ENTITY_ID / endpoint_id

        headers["Authorization"] = self.authorization

        async with httpx.AsyncClient() as client:
            response = await client.get(str(url), headers=headers)

        return response.json()


class AvailableControlPanel:
    """Representation of an available control panel."""

    def __init__(self, hash, online, name):
        """Initialize the new control panel."""
        self.hash = hash
        self.online = online
        self.name = name

    @staticmethod
    def create_new_control_panel(response_entry):
        """Create a new control panel."""
        control_panel = AvailableControlPanel(
            hash=response_entry["hash"],
            online=bool(response_entry["centrale_online"]),
            name=response_entry["username"][0]["label"],
        )
        return control_panel


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
