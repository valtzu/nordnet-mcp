import os
from dataclasses import dataclass


@dataclass
class NordnetConfig:
    session_token: str
    host: str


def load_config() -> NordnetConfig:
    """Load config from environment variables."""
    token = os.environ.get("NORDNET_SESSION_TOKEN")
    host = os.environ.get("NORDNET_HOST", "public.nordnet.se")

    if not token:
        raise ValueError(
            "No session token found. Set NORDNET_SESSION_TOKEN in .env "
            "or as an environment variable."
        )

    return NordnetConfig(session_token=token, host=host)
