from __future__ import annotations

from typing import TypedDict


class EditorOutput(TypedDict):
    edited_caption: str
    edited_slide_text: list[str]
    edited_reel_script: str
    risk_flags: list[str]


EDITOR_OUTPUT_JSON_SCHEMA: dict[str, object] = {
    "name": "editor_output",
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "edited_caption": {"type": "string"},
            "edited_slide_text": {"type": "array", "items": {"type": "string"}},
            "edited_reel_script": {"type": "string"},
            "risk_flags": {"type": "array", "items": {"type": "string"}},
        },
        "required": [
            "edited_caption",
            "edited_slide_text",
            "edited_reel_script",
            "risk_flags",
        ],
    },
}
