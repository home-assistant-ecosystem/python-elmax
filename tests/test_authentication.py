"""Test the authentication process."""
import pytest
from pytest_httpx import HTTPXMock

from elmax import Elmax, exceptions

RESPONSE_AUTHENTICATION_VALID = {
    "token": "JWT 123456.123456",
    "user": {"_id": "1234567", "email": "user@elmax-cloud.test", "role": "user"},
}

RESPONSE_AUTHENTICATION_INVALID = {
    "user": {"_id": "1234567", "email": "user@elmax-cloud.test", "role": "user"},
}

@pytest.mark.asyncio
async def test_authentication_valid(httpx_mock: HTTPXMock):
    """Test a valid authentication process."""
    httpx_mock.add_response(json=RESPONSE_AUTHENTICATION_VALID)

    client = Elmax(username="username", password="password")
    await client.connect()

    assert client.is_authenticated is True


@pytest.mark.asyncio
async def test_authentication_not_json(httpx_mock: HTTPXMock):
    """Test if invalid response is handled correctly."""
    httpx_mock.add_response(json="This is my UTF-8 content")

    with pytest.raises(exceptions.ElmaxConnectionError) as execinfo:
        client = Elmax(username="username", password="password")
        await client.connect()
    
    assert execinfo.value.args[0] == 'Credentials are not valid'
    assert client.is_authenticated is False


@pytest.mark.asyncio
async def test_authentication_incomplete(httpx_mock: HTTPXMock):
    """Test autnetication with an incomplete response."""
    httpx_mock.add_response(json=RESPONSE_AUTHENTICATION_INVALID)

    with pytest.raises(exceptions.ElmaxConnectionError) as execinfo:
        client = Elmax(username="username", password="password")
        await client.connect()
    
    assert execinfo.value.args[0] == 'Credentials are not valid'
    assert client.is_authenticated is False
