from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(slots=True)
class ScheduleRequest:
    post_id: str
    scheduled_for: str
    platform: str = "instagram"


@dataclass(slots=True)
class ScheduledPostResult:
    status: str
    platform_schedule_id: str | None = None


class SchedulerService(Protocol):
    def schedule(self, request: ScheduleRequest) -> ScheduledPostResult:
        ...


class NoOpSchedulerService:
    def schedule(self, request: ScheduleRequest) -> ScheduledPostResult:
        raise NotImplementedError("Add a real publisher or scheduling adapter.")
