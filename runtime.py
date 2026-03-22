from __future__ import annotations

from dataclasses import dataclass
from textwrap import indent
from uuid import uuid4

from agents.approval_agent import ApprovalAgent
from agents.creative_direction_agent import CreativeDirectionAgent
from agents.editor_agent import EditorAgent
from agents.idea_agent import IdeaAgent
from agents.template_finder_agent import TemplateFinderAgent
from agents.template_render_agent import TemplateRenderAgent
from agents.writer_agent import WriterAgent
from config.settings import Settings
from models.post import Post, PostFormat
from models.template import TemplateDefinition
from pipeline.content_pipeline import ContentPipeline
from services.approval_store import SQLiteApprovalStore
from services.openai_service import ResponsesAPIService
from services.placid_service import PlacidService
from services.template_repository import (
    TemplateRepository,
    placid_template_to_definition,
)


@dataclass(slots=True)
class AppRuntime:
    settings: Settings
    pipeline: ContentPipeline
    approval_store: SQLiteApprovalStore


def build_runtime(settings: Settings) -> AppRuntime:
    openai_service = ResponsesAPIService(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        timeout_seconds=settings.http_timeout_seconds,
    )
    renderer_service = PlacidService(
        api_token=settings.placid_api_token,
        base_url=settings.placid_base_url,
        timeout_seconds=settings.http_timeout_seconds,
    )
    approval_store = SQLiteApprovalStore(settings.posts_db_path)

    pipeline = ContentPipeline(
        idea_agent=IdeaAgent(openai_service, settings.openai_model),
        writer_agent=WriterAgent(openai_service, settings.openai_model),
        editor_agent=EditorAgent(openai_service, settings.openai_model),
        creative_direction_agent=CreativeDirectionAgent(
            openai_service, settings.openai_model
        ),
        template_finder_agent=TemplateFinderAgent(),
        template_render_agent=TemplateRenderAgent(
            renderer_service=renderer_service,
            poll_attempts=settings.render_poll_attempts,
            poll_interval_seconds=settings.render_poll_interval_seconds,
        ),
        approval_agent=ApprovalAgent(approval_store),
    )
    return AppRuntime(
        settings=settings,
        pipeline=pipeline,
        approval_store=approval_store,
    )


def load_templates(settings: Settings):
    repository = TemplateRepository(settings.templates_path)
    return repository.load_all()


def fetch_templates(settings: Settings) -> tuple[list[TemplateDefinition], list[str]]:
    """Fetch templates from Placid, with fallback to local. Returns (templates, errors)."""
    from services.placid_service import PlacidService, PlacidServiceError

    templates: list[TemplateDefinition] = []
    errors: list[str] = []

    if settings.placid_api_token:
        try:
            placid = PlacidService(
                api_token=settings.placid_api_token,
                base_url=settings.placid_base_url,
                timeout_seconds=settings.http_timeout_seconds,
            )
            raw = placid.list_templates()
            for item in raw:
                templates.append(placid_template_to_definition(item))
        except PlacidServiceError as e:
            errors.append(str(e))

    if not templates:
        local = load_templates(settings)
        templates.extend(local)
        if not templates and errors:
            errors.append("No local templates found. Add templates to data/templates.json.")

    return templates, errors


def create_post(topic: str, audience: str, format_name: str) -> Post:
    return Post(
        id=str(uuid4()),
        topic=topic,
        audience=audience,
        format=PostFormat(format_name),
    )


def render_post_details(post: Post) -> str:
    lines = [
        f"Post ID: {post.id}",
        f"Status: {post.status.value}",
        f"Topic: {post.topic}",
        f"Audience: {post.audience}",
        f"Format: {post.format.value}",
        f"Title: {post.title or ''}",
        f"Hook: {post.hook or ''}",
        f"Scripture: {post.scripture or ''}",
        f"Angle: {post.angle or ''}",
        f"Caption: {post.caption or ''}",
        f"CTA: {post.cta or ''}",
        f"Hashtags: {', '.join(post.hashtags) if post.hashtags else ''}",
        f"Risk flags: {', '.join(post.risk_flags) if post.risk_flags else 'none'}",
        f"Template ID: {post.template_id or ''}",
        f"Render URL: {post.render_url or ''}",
        f"Review notes: {post.review_notes or ''}",
    ]
    if post.slide_text:
        slide_block = "\n".join(
            f"{index}. {slide}" for index, slide in enumerate(post.slide_text, start=1)
        )
        lines.append("Slides:\n" + indent(slide_block, "  "))
    if post.reel_script:
        lines.append("Reel script:\n" + indent(post.reel_script, "  "))
    return "\n".join(lines)
