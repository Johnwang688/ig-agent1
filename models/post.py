from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum


class PostFormat(StrEnum):
    CAROUSEL = "carousel"
    REEL = "reel"
    QUOTE = "quote"
    VERSE = "verse"


class PostStatus(StrEnum):
    IDEA = "idea"
    DRAFTED = "drafted"
    EDITED = "edited"
    ART_DIRECTED = "art_directed"
    TEMPLATE_SELECTED = "template_selected"
    RENDERED = "rendered"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"


@dataclass(slots=True)
class Post:
    id: str
    topic: str
    audience: str
    format: PostFormat
    angle: str | None = None
    scripture: str | None = None
    hook: str | None = None
    title: str | None = None
    caption: str | None = None
    reel_script: str | None = None
    slide_text: list[str] = field(default_factory=list)
    cta: str | None = None
    hashtags: list[str] = field(default_factory=list)
    risk_flags: list[str] = field(default_factory=list)
    visual_style: str | None = None
    mood: str | None = None
    palette: str | None = None
    composition: str | None = None
    preferred_template_family: str | None = None
    background_type: str | None = None
    renderer: str | None = None
    template_id: str | None = None
    field_map_id: str | None = None
    render_job_id: str | None = None
    render_url: str | None = None
    status: PostStatus = PostStatus.IDEA
    approved_by_human: bool = False
    review_notes: str | None = None
    scheduled_for: str | None = None

    def mark_status(self, status: PostStatus) -> None:
        self.status = status

    def require_human_approval(self) -> None:
        if not self.approved_by_human:
            raise ValueError("Post must be approved by a human before scheduling.")

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Post":
        raw = dict(data)
        raw["format"] = PostFormat(str(raw["format"]))
        raw["status"] = PostStatus(str(raw.get("status", PostStatus.IDEA)))
        raw["slide_text"] = list(raw.get("slide_text", []))
        raw["hashtags"] = list(raw.get("hashtags", []))
        raw["risk_flags"] = list(raw.get("risk_flags", []))
        return cls(**raw)
