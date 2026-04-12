import json

_client = None


def configure(client):
    global _client
    _client = client


def register_tools(app):

    @app.tool()
    async def get_instrument(instrument_id: str) -> str:
        """Get instrument details. Supports comma-separated IDs for batch lookup.

        Args:
            instrument_id: One or more instrument IDs (comma-separated)
        """
        data = await _client.get(f"/instruments/{instrument_id}")
        return json.dumps(data, indent=2)

    @app.tool()
    async def lookup_instrument(lookup_type: str, lookup_value: str) -> str:
        """Find instrument by ISIN+currency+market or market identifier.

        Args:
            lookup_type: "isin_code_currency_market_id" or "market_id_identifier"
            lookup_value: For ISIN: "ISIN:CURRENCY:MARKET_ID" (e.g. "NO0010096985:NOK:15").
                          For market: "MARKET_ID:IDENTIFIER" (e.g. "15:2274236").
                          Comma-separate for batch lookup.
        """
        data = await _client.get(
            f"/instruments/lookup/{lookup_type}/{lookup_value}"
        )
        return json.dumps(data, indent=2)

    @app.tool()
    async def search_stocks(query: str, limit: int = 20) -> str:
        """Search Nordnet's stock database with free text.

        Args:
            query: Search text (company name, ticker, etc.)
            limit: Max results (default 20)
        """
        data = await _client.get(
            "/instrument_search/query/stocklist",
            params={"query": query, "limit": limit},
        )
        return json.dumps(data, indent=2)

    @app.tool()
    async def check_suitability(instrument_id: int) -> str:
        """Check if an instrument is tradeable for your account.

        Args:
            instrument_id: The instrument ID to check
        """
        data = await _client.get(
            f"/instruments/validation/suitability/{instrument_id}"
        )
        return json.dumps(data, indent=2)

    return app
