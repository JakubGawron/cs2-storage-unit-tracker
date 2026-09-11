import json
from dataclasses import dataclass, field
from typing import Any, Literal

import requests
from pydantic import HttpUrl

from cs2_storage_unit_tracker.config import API_DEFAULTS
from cs2_storage_unit_tracker.helpers.errors import (
    ApiRequestError,
    ApiResponseError,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class ApiClient:
    url: HttpUrl | None = None
    max_response_size: int = API_DEFAULTS.max_response_size
    chunk_size: int = API_DEFAULTS.chunk_size
    session: requests.Session = field(default_factory=requests.Session, repr=False)

    def __post_init__(self) -> None:
        self.session.headers.update(API_DEFAULTS.headers)

    def close(self) -> None:
        self.session.close()

    def request(self, method: Literal["GET"], **kwargs: Any) -> Any:
        kwargs.setdefault("timeout", API_DEFAULTS.timeout)
        try:
            with self.session.request(
                method=method, stream=True, url=str(self.url), **kwargs
            ) as response:
                response.raise_for_status()

                content_type: str = response.headers.get("Content-Type", "")
                if "application/json" not in content_type:
                    raise ApiResponseError(
                        "Expected a JSON response with Content-Type: 'application/json'"
                    )

                response_size_error: str = (
                    f"Response too large (bigger than {self.max_response_size} B)"
                )
                content_length: str = response.headers.get("Content-Length", "")

                if (
                    content_length.isdigit()
                    and int(content_length) > self.max_response_size
                ):
                    raise ApiResponseError(response_size_error)

                chunks = bytearray()
                for chunk in response.iter_content(chunk_size=self.chunk_size):
                    chunks.extend(chunk)

                    if len(chunks) > self.max_response_size:
                        raise ApiResponseError(response_size_error)

                data: Any = json.loads(chunks)
                return data

        except json.JSONDecodeError as exc:
            raise ApiResponseError("API returned invalid JSON") from exc

        except requests.exceptions.RequestException as exc:
            raise ApiRequestError("API request failed") from exc

    def get(self, **kwargs: Any) -> Any:
        return self.request("GET", **kwargs)

    def scoped(self, url: HttpUrl, **kwargs: Any) -> ApiClient:
        return ApiClient(
            url=url,
            session=self.session,
            max_response_size=kwargs.get("max_response_size", self.max_response_size),
            chunk_size=kwargs.get("chunk_size", self.chunk_size),
        )
