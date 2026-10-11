import os
from functools import lru_cache


@lru_cache
def get_settings():
    return {
        "database_url": os.getenv("DATABASE_URL", "sqlite:///./sprintdesk.db"),
        "secret_key": os.getenv("SECRET_KEY", "local-development-only-change-for-production"),
        "token_ttl": int(os.getenv("TOKEN_TTL", "86400")),
    }
