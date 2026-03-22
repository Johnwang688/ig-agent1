from __future__ import annotations

from typing import Literal, TypedDict


class IdeaOutput(TypedDict):
    angle: str
    scripture: str
    hook: str
    title: str
    format: Literal["carousel", "reel", "quote", "verse"]


IDEA_OUTPUT_JSON_SCHEMA: dict[str, object] = {
    "name": "idea_output",
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "angle": {"type": "string"},
            "scripture": {"type": "string"},
            "hook": {"type": "string"},
            "title": {"type": "string"},
            "format": {
                "type": "string",
                "enum": ["carousel", "reel", "quote", "verse"],
            },
        },
        "required": ["angle", "scripture", "hook", "title", "format"],
    },
}
