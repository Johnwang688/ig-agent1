from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from models.post import Post, PostStatus


@dataclass(slots=True)
class ApprovalRecord:
    post_id: str
    approved_by_human: bool
    review_notes: str | None = None


class ApprovalStore(Protocol):
    def save_post(self, post: Post) -> None:
        ...

    def get_post(self, post_id: str) -> Post | None:
        ...

    def record_review(self, record: ApprovalRecord) -> None:
        ...

    def list_posts(self, status: PostStatus | None = None) -> list[Post]:
        ...

    def list_pending_review(self) -> list[Post]:
        ...


class SQLiteApprovalStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def save_post(self, post: Post) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO posts (
                    id, status, approved_by_human, topic, audience, format, content_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    status = excluded.status,
                    approved_by_human = excluded.approved_by_human,
                    topic = excluded.topic,
                    audience = excluded.audience,
                    format = excluded.format,
                    content_json = excluded.content_json,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    post.id,
                    post.status.value,
                    int(post.approved_by_human),
                    post.topic,
                    post.audience,
                    post.format.value,
                    json.dumps(post.to_dict()),
                ),
            )

    def get_post(self, post_id: str) -> Post | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT content_json FROM posts WHERE id = ?",
                (post_id,),
            ).fetchone()
        if row is None:
            return None
        return Post.from_dict(json.loads(row["content_json"]))

    def record_review(self, record: ApprovalRecord) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO reviews (post_id, approved_by_human, review_notes)
                VALUES (?, ?, ?)
                """,
                (record.post_id, int(record.approved_by_human), record.review_notes),
            )

    def list_posts(self, status: PostStatus | None = None) -> list[Post]:
        query = "SELECT content_json FROM posts"
        params: tuple[object, ...] = ()
        if status is not None:
            query += " WHERE status = ?"
            params = (status.value,)
        query += " ORDER BY updated_at DESC, created_at DESC"

        with self._connect() as connection:
            rows = connection.execute(query, params).fetchall()
        return [Post.from_dict(json.loads(row["content_json"])) for row in rows]

    def list_pending_review(self) -> list[Post]:
        return self.list_posts(PostStatus.IN_REVIEW)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS posts (
                    id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    approved_by_human INTEGER NOT NULL DEFAULT 0,
                    topic TEXT NOT NULL,
                    audience TEXT NOT NULL,
                    format TEXT NOT NULL,
                    content_json TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_id TEXT NOT NULL,
                    approved_by_human INTEGER NOT NULL,
                    review_notes TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
