# tests/test_reference.py
import json
from unittest.mock import AsyncMock

import pytest

from nordnet_mcp.reference import configure, register_tools


@pytest.fixture
def mock_client():
    client = AsyncMock()
    client.get = AsyncMock()
    return client


@pytest.fixture
def app(mock_client):
    from mcp.server.fastmcp import FastMCP
    app = FastMCP("test")
    configure(mock_client)
    return register_tools(app)


@pytest.mark.asyncio
async def test_all_reference_tools_registered(app):
    tools = {t.name for t in await app.list_tools()}
    assert "get_countries" in tools
    assert "get_instrument_types" in tools
    assert "get_search_attributes" in tools


@pytest.mark.asyncio
async def test_get_countries(mock_client, app):
    mock_client.get.return_value = [{"code": "NO", "name": "Norway"}]

    content, _meta = await app.call_tool("get_countries", {})
    data = json.loads(content[0].text)
    assert data[0]["code"] == "NO"
