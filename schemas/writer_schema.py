from __future__ import annotations

from typing import TypedDict


class WriterOutput(TypedDict):
    caption: str
    slide_text: list[str]
    reel_script: str
    cta: str
    hashtags: list[str]


WRITER_OUTPUT_JSON_SCHEMA: dict[str, object] = {
    "name": "writer_output",
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "caption": {"type": "string"},
            "slide_text": {"type": "array", "items": {"type": "string"}},
            "reel_script": {"type": "string"},
            "cta": {"type": "string"},
            "hashtags": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["caption", "slide_text", "reel_script", "cta", "hashtags"],
    },
}
