from __future__ import annotations

import time

from models.post import Post, PostStatus
from models.template import TemplateDefinition
from services.placid_service import RenderRequest, TemplateRendererService
from services.template_validation import validate_template_fit


class TemplateRenderAgent:
    def __init__(
        self,
        renderer_service: TemplateRendererService,
        poll_attempts: int = 10,
        poll_interval_seconds: int = 3,
    ) -> None:
        self.renderer_service = renderer_service
        self.poll_attempts = poll_attempts
        self.poll_interval_seconds = poll_interval_seconds

    def run(self, post: Post, template: TemplateDefinition) -> Post:
        validate_template_fit(post, template)
        layers: dict[str, dict[str, object]] = {}

        for semantic_field, layer_name in template.layer_map.items():
            value = getattr(post, semantic_field, None)
            if value:
                if semantic_field.endswith("_image_url"):
                    layers[layer_name] = {"image": value}
                else:
                    layers[layer_name] = {"text": value}

        result = self.renderer_service.render(
            RenderRequest(
                template_id=template.id,
                layers=layers,
                width=1080,
                height=1350,
            )
        )
        post.render_job_id = result.job_id
        post.render_url = result.image_url

        if not post.render_url:
            for _ in range(self.poll_attempts):
                time.sleep(self.poll_interval_seconds)
                status = self.renderer_service.get_render_status(result.job_id)
                post.render_url = status.image_url
                if post.render_url or status.status == "error":
                    break

        if not post.render_url:
            post.status = PostStatus.FAILED
            raise ValueError(f"Render did not complete successfully for job {result.job_id}.")

        post.status = PostStatus.RENDERED
        return post
