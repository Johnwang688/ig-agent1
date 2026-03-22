from __future__ import annotations

from models.post import Post, PostStatus
from services.approval_store import ApprovalRecord, ApprovalStore


class ApprovalAgent:
    def __init__(self, approval_store: ApprovalStore) -> None:
        self.approval_store = approval_store

    def submit_for_review(self, post: Post) -> Post:
        post.status = PostStatus.IN_REVIEW
        self.approval_store.save_post(post)
        return post

    def review(self, post: Post, approved: bool, notes: str | None = None) -> Post:
        post.approved_by_human = approved
        post.review_notes = notes
        post.status = PostStatus.APPROVED if approved else PostStatus.REJECTED
        self.approval_store.record_review(
            ApprovalRecord(
                post_id=post.id,
                approved_by_human=approved,
                review_notes=notes,
            )
        )
        self.approval_store.save_post(post)
        return post
