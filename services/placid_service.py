from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Protocol
from urllib import error, request


class PlacidServiceError(RuntimeError):
    pass


@dataclass(slots=True)
class RenderRequest:
    template_id: str
    layers: dict[str, dict[str, object]]
    width: int
    height: int
    background_image_url: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class RenderResult:
    job_id: str
    status: str
    image_url: str | None = None
    raw_response: dict[str, object] = field(default_factory=dict)


class TemplateRendererService(Protocol):
    def render(self, request: RenderRequest) -> RenderResult:
        ...

    def get_render_status(self, job_id: str) -> RenderResult:
        ...

    def resolve_final_url(self, job_id: str) -> str:
        ...


class PlacidService:
    def __init__(
        self,
        api_token: str,
        base_url: str = "https://api.placid.app/api/rest",
        timeout_seconds: int = 60,
    ) -> None:
        self.api_token = api_token
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def render(self, render_request: RenderRequest) -> RenderResult:
        payload = {
            "template_uuid": render_request.template_id,
            "layers": render_request.layers,
            "modifications": {
                "width": render_request.width,
                "height": render_request.height,
            },
        }
        if render_request.background_image_url:
            payload["layers"]["background_image"] = {
                "image": render_request.background_image_url
            }

        response = self._request_json("POST", "/images", payload)
        return self._parse_render_result(response)

    def get_render_status(self, job_id: str) -> RenderResult:
        response = self._request_json("GET", f"/images/{job_id}")
        return self._parse_render_result(response)

    def list_templates(
        self,
        tag: str | None = None,
        title_filter: str | None = None,
        per_page: int = 100,
    ) -> list[dict[str, object]]:
        params: list[str] = [f"per_page={per_page}"]
        if tag:
            params.append(f"tag={tag}")
        if title_filter:
            params.append(f"title_filter={title_filter}")
        path = "/templates"
        if params:
            path += "?" + "&".join(params)

        response = self._request_json("GET", path)
        data = response.get("data", [])
        if not isinstance(data, list):
            return []
        return [item for item in data if isinstance(item, dict)]

    def resolve_final_url(self, job_id: str) -> str:
        result = self.get_render_status(job_id)
        if not result.image_url:
            raise PlacidServiceError(f"Render {job_id} has no final image URL yet.")
        return result.image_url

    def _request_json(
        self,
        method: str,
        path: str,
        payload: dict[str, object] | None = None,
    ) -> dict[str, object]:
        if not self.api_token:
            raise PlacidServiceError("PLACID_API_TOKEN is not configured.")

        raw_data = None
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Accept": "application/json",
        }
        if payload is not None:
            raw_data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        http_request = request.Request(
            url=f"{self.base_url}{path}",
            data=raw_data,
            headers=headers,
            method=method,
        )

        try:
            with request.urlopen(http_request, timeout=self.timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            raise PlacidServiceError(
                f"Placid request failed with HTTP {exc.code}: {details}"
            ) from exc
        except error.URLError as exc:
            raise PlacidServiceError(f"Unable to reach Placid: {exc.reason}") from exc

    def _parse_render_result(self, response: dict[str, object]) -> RenderResult:
        job_id = response.get("id")
        if job_id is None:
            raise PlacidServiceError(f"Missing render job id in response: {response}")

        return RenderResult(
            job_id=str(job_id),
            status=str(response.get("status", "unknown")),
            image_url=(
                str(response["image_url"]) if response.get("image_url") is not None else None
            ),
            raw_response=response,
        )
