from __future__ import annotations

from models.post import Post, PostStatus
from prompts.writer_prompt import build_writer_prompt
from schemas.writer_schema import WRITER_OUTPUT_JSON_SCHEMA
from services.openai_service import OpenAIService, StructuredGenerationRequest


class WriterAgent:
    def __init__(self, openai_service: OpenAIService, model: str) -> None:
        self.openai_service = openai_service
        self.model = model

    def run(self, post: Post) -> Post:
        prompt = build_writer_prompt(
            angle=post.angle or "",
            scripture=post.scripture or "",
            hook=post.hook or "",
            title=post.title or "",
            format_name=post.format.value,
        )
        result = self.openai_service.generate_structured(
            StructuredGenerationRequest(
                prompt=prompt,
                schema=WRITER_OUTPUT_JSON_SCHEMA,
                model=self.model,
                metadata={"agent": "writer"},
            )
        )
        post.caption = str(result["caption"])
        post.slide_text = [str(item) for item in result["slide_text"]]
        post.reel_script = str(result["reel_script"])
        post.cta = str(result["cta"])
        post.hashtags = [str(item) for item in result["hashtags"]]
        post.status = PostStatus.DRAFTED
        return post
