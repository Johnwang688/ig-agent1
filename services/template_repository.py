from __future__ import annotations

import json
from pathlib import Path

from models.template import TemplateDefinition


# Heuristic: map Placid layer names (normalized) to our semantic fields
_SEMANTIC_MATCHES: dict[str, list[str]] = {
    "title": ["title", "headline", "heading", "head"],
    "caption": ["caption", "subhead", "subtitle", "subheadline", "body", "text"],
    "scripture": ["scripture", "verse", "reference", "bible", "passage"],
    "cta": ["cta", "footer", "call_to_action", "call", "button", "action"],
}


def _infer_layer_map(placid_layers: list[object]) -> dict[str, str]:
    layer_map: dict[str, str] = {}
    for layer in placid_layers:
        if not isinstance(layer, dict):
            continue
        raw_name = layer.get("name")
        layer_type = layer.get("type", "")
        if not raw_name or not isinstance(raw_name, str):
            continue
        if layer_type == "picture":
            continue
        normalized = raw_name.lower().replace(" ", "_").replace("-", "_")
        for semantic_field, patterns in _SEMANTIC_MATCHES.items():
            if semantic_field in layer_map:
                continue
            if any(p in normalized or normalized in p for p in patterns):
                layer_map[semantic_field] = raw_name
                break
    return layer_map


def placid_template_to_definition(
    placid_item: dict[str, object],
    format_hint: str = "carousel",
) -> TemplateDefinition:
    uuid_val = str(placid_item.get("uuid", ""))
    title_val = str(placid_item.get("title", "Untitled"))
    tags = placid_item.get("tags") or []
    if isinstance(tags, list):
        tags = [str(t) for t in tags]
    else:
        tags = []
    layers_raw = placid_item.get("layers") or []
    if isinstance(layers_raw, list):
        layer_map = _infer_layer_map(layers_raw)
    else:
        layer_map = {}
    format_str = format_hint
    for tag in tags:
        t = str(tag).lower()
        if t in ("carousel", "reel", "quote", "verse", "instagram", "post"):
            format_str = "reel" if t == "reel" else "carousel"
            break
    return TemplateDefinition(
        id=uuid_val,
        renderer="placid",
        format=format_str,
        style_family=title_val[:40] or "unknown",
        max_title_chars=80,
        max_subtitle_chars=200,
        max_cta_chars=50,
        max_verse_chars=80,
        layer_map=layer_map,
    )


class TemplateRepository:
    def __init__(self, templates_path: Path) -> None:
        self.templates_path = templates_path

    def load_all(self) -> list[TemplateDefinition]:
        if not self.templates_path.exists():
            return []
        with self.templates_path.open("r", encoding="utf-8") as file_handle:
            raw_templates = json.load(file_handle)
        return [TemplateDefinition.from_dict(item) for item in raw_templates]

    def get_by_id(self, template_id: str) -> TemplateDefinition | None:
        for template in self.load_all():
            if template.id == template_id:
                return template
        return None
