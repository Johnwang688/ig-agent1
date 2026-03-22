from __future__ import annotations

from models.post import Post, PostStatus
from models.template import TemplateDefinition


class TemplateFinderAgent:
    def run(self, post: Post, templates: list[TemplateDefinition]) -> Post:
        def _normalize(s: str) -> str:
            return s.lower().replace(" ", "_").replace("-", "_")

        matching_templates = [
            template
            for template in templates
            if template.format == post.format.value
            and (
                not post.preferred_template_family
                or _normalize(template.style_family)
                    == _normalize(post.preferred_template_family)
            )
        ]
        if not matching_templates:
            matching_templates = [
                t for t in templates if t.format == post.format.value
            ]
        if not matching_templates:
            raise ValueError(f"No template found for format={post.format.value!r}")

        selected = matching_templates[0]
        post.renderer = selected.renderer
        post.template_id = selected.id
        post.field_map_id = selected.id
        post.status = PostStatus.TEMPLATE_SELECTED
        return post
