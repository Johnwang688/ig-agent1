from __future__ import annotations

from typing import TypedDict


class CreativeDirectionOutput(TypedDict):
    visual_style: str
    mood: str
    palette: str
    composition: str
    preferred_template_family: str
    background_type: str


CREATIVE_DIRECTION_JSON_SCHEMA: dict[str, object] = {
    "name": "creative_direction_output",
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "visual_style": {"type": "string"},
            "mood": {"type": "string"},
            "palette": {"type": "string"},
            "composition": {"type": "string"},
            "preferred_template_family": {"type": "string"},
            "background_type": {"type": "string"},
        },
        "required": [
            "visual_style",
            "mood",
            "palette",
            "composition",
            "preferred_template_family",
            "background_type",
        ],
    },
}
