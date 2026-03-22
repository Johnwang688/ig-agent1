from __future__ import annotations

from models.post import Post
from models.template import TemplateDefinition


def validate_template_fit(post: Post, template: TemplateDefinition) -> None:
    for semantic_field in template.layer_map:
        value = getattr(post, semantic_field, None)
        if not value or not isinstance(value, str):
            continue

        char_limit = template.field_char_limit(semantic_field)
        if char_limit and len(value) > char_limit:
            raise ValueError(
                f"Field {semantic_field!r} exceeds template limit "
                f"({len(value)} > {char_limit}) for template {template.id!r}."
            )
