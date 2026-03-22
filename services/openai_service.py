from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Protocol
from urllib import error, request


class OpenAIServiceError(RuntimeError):
    pass


@dataclass(slots=True)
class StructuredGenerationRequest:
    prompt: str
    schema: dict[str, object]
    model: str
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class TextGenerationRequest:
    prompt: str
    model: str
    metadata: dict[str, str] = field(default_factory=dict)


class OpenAIService(Protocol):
    def generate_structured(
        self, request: StructuredGenerationRequest
    ) -> dict[str, object]:
        ...

    def generate_text(self, request: TextGenerationRequest) -> str:
        ...


class ResponsesAPIService:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.openai.com/v1",
        timeout_seconds: int = 60,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def generate_structured(
        self, structured_request: StructuredGenerationRequest
    ) -> dict[str, object]:
        schema_name = str(structured_request.schema["name"])
        schema_body = structured_request.schema["schema"]
        base_payload = {
            "model": structured_request.model,
            "input": structured_request.prompt,
        }

        try:
            response = self._request_json(
                payload={
                    **base_payload,
                    "text": {
                        "format": {
                            "type": "json_schema",
                            "name": schema_name,
                            "strict": True,
                            "schema": schema_body,
                        }
                    },
                }
            )
            output_text = self._extract_output_text(response)
            return self._decode_json_output(output_text)
        except OpenAIServiceError as exc:
            message = str(exc)
            if "Unsupported parameter" not in message and "Unknown parameter" not in message:
                raise
            response = self._request_json(
                payload={
                    **base_payload,
                    "response_format": {
                        "type": "json_schema",
                        "json_schema": {
                            "name": schema_name,
                            "strict": True,
                            "schema": schema_body,
                        },
                    },
                }
            )
            output_text = self._extract_output_text(response)
            return self._decode_json_output(output_text)

    def generate_text(self, text_request: TextGenerationRequest) -> str:
        response = self._request_json(
            payload={
                "model": text_request.model,
                "input": text_request.prompt,
            }
        )
        return self._extract_output_text(response)

    def _request_json(self, payload: dict[str, object]) -> dict[str, object]:
        if not self.api_key:
            raise OpenAIServiceError("OPENAI_API_KEY is not configured.")

        raw_data = json.dumps(payload).encode("utf-8")
        http_request = request.Request(
            url=f"{self.base_url}/responses",
            data=raw_data,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )

        try:
            with request.urlopen(http_request, timeout=self.timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            raise OpenAIServiceError(
                f"OpenAI request failed with HTTP {exc.code}: {details}"
            ) from exc
        except error.URLError as exc:
            raise OpenAIServiceError(f"Unable to reach OpenAI: {exc.reason}") from exc

    def _extract_output_text(self, response: dict[str, object]) -> str:
        output_text = response.get("output_text")
        if isinstance(output_text, str) and output_text:
            return output_text

        output = response.get("output", [])
        if not isinstance(output, list):
            raise OpenAIServiceError(f"Unexpected Responses API shape: {response}")

        fragments: list[str] = []
        for item in output:
            if not isinstance(item, dict):
                continue
            for content_item in item.get("content", []):
                if not isinstance(content_item, dict):
                    continue
                if content_item.get("type") == "output_text":
                    text_value = content_item.get("text")
                    if isinstance(text_value, str):
                        fragments.append(text_value)
                if content_item.get("type") == "refusal":
                    refusal = content_item.get("refusal", "Request refused.")
                    raise OpenAIServiceError(str(refusal))

        if fragments:
            return "".join(fragments)

        raise OpenAIServiceError(f"No output text found in OpenAI response: {response}")

    def _decode_json_output(self, output_text: str) -> dict[str, object]:
        try:
            return json.loads(output_text)
        except json.JSONDecodeError as exc:
            raise OpenAIServiceError(
                f"OpenAI returned non-JSON structured output: {output_text}"
            ) from exc
