"""Constants for the Elmax Cloud service client."""

BASE_URL = "https://cloud.elmaxsrl.it"

ENDPOINT_DEVICES = "api/ext/devices"
ENDPOINT_LOGIN = "api/ext/login"
ENDPOINT_STATUS_ENTITY_ID = "api/ext/status"
ENDPOINT_ENTITY_ID_COMMAND = "api/ext"
ENDPOINT_DISCOVERY = "api/ext/discovery"

version = "0.1.0-test-client"

USER_AGENT= f"PythonElmax/{version}"

COMMAND_ON = "on"
COMMAND_OFF = "off"

COMMAND_ARM = "ins"
COMMAND_DISARM = "dis"

ZONE = "zone"
OUTPUT = "uscite"
AREA = "aree"

UNIT_TYPES = [
    AREA,
    OUTPUT,
    ZONE,
]
