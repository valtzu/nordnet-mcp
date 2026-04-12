import json
from unittest.mock import AsyncMock

import pytest

from nordnet_mcp.instruments import configure, register_tools

MOCK_INSTRUMENT = {
    "instrument_id": 16120194,
    "name": "Novo Nordisk B",
    "isin_code": "DK0062498333",
    "symbol": "NOVO B",
    "currency": "DKK",
    "instrument_type": "ESH",
    "tradables": [{"market_id": 19, "identifier": "NOVO+B"}],
}

MOCK_SEARCH = [
    {"instrument_id": 16120194, "name": "Novo Nordisk B", "symbol": "NOVO B"},
    {"instrument_id": 16120195, "name": "Novo Nordisk A", "symbol": "NOVO A"},
]


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
async def test_get_instrument(mock_client, app):
    mock_client.get.return_value = [MOCK_INSTRUMENT]

    content, _meta = await app.call_tool("get_instrument", {"instrument_id": "16120194"})
    data = json.loads(content[0].text)
    assert data[0]["name"] == "Novo Nordisk B"


@pytest.mark.asyncio
async def test_search_stocks(mock_client, app):
    mock_client.get.return_value = MOCK_SEARCH

    content, _meta = await app.call_tool("search_stocks", {"query": "novo"})
    data = json.loads(content[0].text)
    assert len(data) == 2


@pytest.mark.asyncio
async def test_lookup_instrument(mock_client, app):
    mock_client.get.return_value = [MOCK_INSTRUMENT]

    content, _meta = await app.call_tool("lookup_instrument", {
        "lookup_type": "isin_code_currency_market_id",
        "lookup_value": "DK0062498333:DKK:19",
    })
    data = json.loads(content[0].text)
    assert data[0]["isin_code"] == "DK0062498333"

    mock_client.get.assert_called_with(
        "/instruments/lookup/isin_code_currency_market_id/DK0062498333:DKK:19"
    )
