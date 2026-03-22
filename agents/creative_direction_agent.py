from __future__ import annotations

from models.post import Post, PostStatus
from prompts.creative_prompt import build_creative_prompt
from schemas.creative_schema import CREATIVE_DIRECTION_JSON_SCHEMA
from services.openai_service import OpenAIService, StructuredGenerationRequest


class CreativeDirectionAgent:
    def __init__(self, openai_service: OpenAIService, model: str) -> None:
        self.openai_service = openai_service
        self.model = model

    def run(self, post: Post) -> Post:
        prompt = build_creative_prompt(
            format_name=post.format.value,
            title=post.title or "",
            caption=post.caption or "",
            slide_text=post.slide_text,
        )
        result = self.openai_service.generate_structured(
            StructuredGenerationRequest(
                prompt=prompt,
                schema=CREATIVE_DIRECTION_JSON_SCHEMA,
                model=self.model,
                metadata={"agent": "creative_direction"},
            )
        )
        post.visual_style = str(result["visual_style"])
        post.mood = str(result["mood"])
        post.palette = str(result["palette"])
        post.composition = str(result["composition"])
        post.preferred_template_family = str(result["preferred_template_family"])
        post.background_type = str(result["background_type"])
        post.status = PostStatus.ART_DIRECTED
        return post
