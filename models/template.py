from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(slots=True)
class TemplateDefinition:
    id: str
    renderer: str
    format: str
    style_family: str
    max_title_chars: int = 0
    max_subtitle_chars: int = 0
    max_cta_chars: int = 0
    max_verse_chars: int = 0
    layer_map: dict[str, str] = field(default_factory=dict)

    def field_char_limit(self, field_name: str) -> int | None:
        aliases = {
            "caption": "subtitle",
            "scripture": "verse",
        }
        field_name = aliases.get(field_name, field_name)
        key = f"max_{field_name}_chars"
        return getattr(self, key, None)

    def supports_field(self, field_name: str) -> bool:
        return field_name in self.layer_map

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "TemplateDefinition":
        raw = dict(data)
        raw["layer_map"] = dict(raw.get("layer_map", {}))
        return cls(**raw)
