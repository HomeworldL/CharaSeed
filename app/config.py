from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    app_name: str = "CharaSeed"
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./charaseed.db")
    zerochan_user_agent: str = os.getenv(
        "ZEROCHAN_USER_AGENT",
        "CharaSeed MVP - ZerochanDemo",
    )
    request_timeout_seconds: float = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "12"))
    site_request_timeout_seconds: float = float(os.getenv("SITE_REQUEST_TIMEOUT_SECONDS", "6"))
    search_cache_ttl_seconds: float = float(os.getenv("SEARCH_CACHE_TTL_SECONDS", "90"))
    http_trust_env: bool = os.getenv("HTTP_TRUST_ENV", "1") != "0"


settings = Settings()
