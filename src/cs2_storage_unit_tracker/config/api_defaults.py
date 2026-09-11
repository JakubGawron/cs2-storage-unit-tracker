from dataclasses import dataclass
from types import MappingProxyType


@dataclass(frozen=True, slots=True, kw_only=True)
class ApiDefaults:
    headers: MappingProxyType[str, str] = MappingProxyType(
        {
            "Accept": "application/json",
            "User-Agent": "curl/8.21.0",
        }
    )
    timeout: int = 10
    max_response_size: int = 1024
    chunk_size: int = 256


API_DEFAULTS = ApiDefaults()
