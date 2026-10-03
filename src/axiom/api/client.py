from dataclasses import dataclass
import requests


@dataclass
class APIResponse:
    status_code: int
    data: dict


class ExternalAPIClient:
    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        timeout: int = 20,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def post(
        self,
        endpoint: str,
        payload: dict,
    ) -> APIResponse:

        headers = {
            "Content-Type": "application/json",
        }

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        response = requests.post(
            f"{self.base_url}/{endpoint.lstrip('/')}",
            json=payload,
            headers=headers,
            timeout=self.timeout,
        )

        response.raise_for_status()

        return APIResponse(
            status_code=response.status_code,
            data=response.json(),
        )