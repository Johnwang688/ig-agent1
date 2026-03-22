from __future__ import annotations

from models.post import Post, PostFormat, PostStatus
from prompts.idea_prompt import build_idea_prompt
from schemas.idea_schema import IDEA_OUTPUT_JSON_SCHEMA
from services.openai_service import OpenAIService, StructuredGenerationRequest


class IdeaAgent:
    def __init__(self, openai_service: OpenAIService, model: str) -> None:
        self.openai_service = openai_service
        self.model = model

    def run(self, post: Post) -> Post:
        prompt = build_idea_prompt(post.topic, post.audience, post.format.value)
        result = self.openai_service.generate_structured(
            StructuredGenerationRequest(
                prompt=prompt,
                schema=IDEA_OUTPUT_JSON_SCHEMA,
                model=self.model,
                metadata={"agent": "idea"},
            )
        )
        post.angle = str(result["angle"])
        post.scripture = str(result["scripture"])
        post.hook = str(result["hook"])
        post.title = str(result["title"])
        post.format = PostFormat(str(result["format"]))
        post.status = PostStatus.DRAFTED
        return post
