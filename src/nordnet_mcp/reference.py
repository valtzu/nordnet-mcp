# src/nordnet_mcp/reference.py
import json

_client = None


def configure(client):
    global _client
    _client = client


def register_tools(app):

    @app.tool()
    async def get_countries() -> str:
        """Get list of countries available on Nordnet."""
        data = await _client.get("/countries")
        return json.dumps(data, indent=2)

    @app.tool()
    async def get_instrument_types() -> str:
        """Get all available instrument types (stocks, ETFs, bonds, etc.)."""
        data = await _client.get("/instruments/types")
        return json.dumps(data, indent=2)

    @app.tool()
    async def get_search_attributes() -> str:
        """Get available search filter attributes for instrument search."""
        data = await _client.get("/instrument_search/attributes")
        return json.dumps(data, indent=2)

    return app
