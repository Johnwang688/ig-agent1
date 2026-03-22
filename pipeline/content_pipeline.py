from __future__ import annotations

from dataclasses import dataclass

from agents.approval_agent import ApprovalAgent
from agents.creative_direction_agent import CreativeDirectionAgent
from agents.editor_agent import EditorAgent
from agents.idea_agent import IdeaAgent
from agents.template_finder_agent import TemplateFinderAgent
from agents.template_render_agent import TemplateRenderAgent
from agents.writer_agent import WriterAgent
from models.post import Post
from models.template import TemplateDefinition


@dataclass(slots=True)
class PipelineRunResult:
    post: Post
    risk_flags: list[str]


class ContentPipeline:
    def __init__(
        self,
        idea_agent: IdeaAgent,
        writer_agent: WriterAgent,
        editor_agent: EditorAgent,
        creative_direction_agent: CreativeDirectionAgent,
        template_finder_agent: TemplateFinderAgent,
        template_render_agent: TemplateRenderAgent,
        approval_agent: ApprovalAgent,
    ) -> None:
        self.idea_agent = idea_agent
        self.writer_agent = writer_agent
        self.editor_agent = editor_agent
        self.creative_direction_agent = creative_direction_agent
        self.template_finder_agent = template_finder_agent
        self.template_render_agent = template_render_agent
        self.approval_agent = approval_agent

    def generate(
        self,
        post: Post,
        templates: list[TemplateDefinition],
        selected_template_id: str | None = None,
    ) -> PipelineRunResult:
        post = self.idea_agent.run(post)
        post = self.writer_agent.run(post)
        post, risk_flags = self.editor_agent.run(post)
        post = self.creative_direction_agent.run(post)

        if selected_template_id:
            selected_template = next(
                (t for t in templates if t.id == selected_template_id),
                None,
            )
            if not selected_template:
                raise ValueError(f"Template {selected_template_id!r} not found.")
            post.template_id = selected_template_id
            post.renderer = selected_template.renderer
            post.field_map_id = selected_template.id
        else:
            post = self.template_finder_agent.run(post, templates)
            selected_template = next(
                t for t in templates if t.id == post.template_id
            )

        post = self.template_render_agent.run(post, selected_template)
        post = self.approval_agent.submit_for_review(post)
        return PipelineRunResult(post=post, risk_flags=risk_flags)
