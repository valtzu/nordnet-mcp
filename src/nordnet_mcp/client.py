import base64

import httpx


class SessionExpiredError(Exception):
    pass


class NordnetClient:
    def __init__(self, session_token: str, host: str = "public.nordnet.se"):
        self.base_url = f"https://{host}/api/2"
        self.session_token = session_token
        self._client = httpx.AsyncClient()

    def _auth_header(self) -> dict:
        creds = base64.b64encode(
            f"{self.session_token}:{self.session_token}".encode()
        ).decode()
        return {"Authorization": f"Basic {creds}"}

    async def get(self, path: str, params: dict | None = None) -> dict | list:
        resp = await self._client.get(
            f"{self.base_url}{path}",
            headers=self._auth_header(),
            params=params,
        )
        if resp.status_code == 401:
            raise SessionExpiredError(
                "Session expired. Refresh your token:\n"
                "1. Log into nordnet.se\n"
                "2. Open DevTools → Application/Storage → Cookies\n"
                "3. Select the Nordnet domain and find NNX_SESSION_ID\n"
                "4. Copy that cookie value into NORDNET_SESSION_TOKEN"
            )
        resp.raise_for_status()
        if not resp.content:
            return []
        return resp.json()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        await self.close()

    async def close(self):
        await self._client.aclose()
