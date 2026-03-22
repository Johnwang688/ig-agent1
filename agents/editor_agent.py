from __future__ import annotations

from models.post import Post, PostStatus
from prompts.editor_prompt import build_editor_prompt
from schemas.editor_schema import EDITOR_OUTPUT_JSON_SCHEMA
from services.openai_service import OpenAIService, StructuredGenerationRequest


class EditorAgent:
    def __init__(self, openai_service: OpenAIService, model: str) -> None:
        self.openai_service = openai_service
        self.model = model

    def run(self, post: Post) -> tuple[Post, list[str]]:
        prompt = build_editor_prompt(
            caption=post.caption or "",
            slide_text=post.slide_text,
            reel_script=post.reel_script or "",
        )
        result = self.openai_service.generate_structured(
            StructuredGenerationRequest(
                prompt=prompt,
                schema=EDITOR_OUTPUT_JSON_SCHEMA,
                model=self.model,
                metadata={"agent": "editor"},
            )
        )
        post.caption = str(result["edited_caption"])
        post.slide_text = [str(item) for item in result["edited_slide_text"]]
        post.reel_script = str(result["edited_reel_script"])
        post.risk_flags = [str(item) for item in result["risk_flags"]]
        post.status = PostStatus.EDITED
        return post, post.risk_flags
