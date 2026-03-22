from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class AnalyticsSummary:
    weekly_summary: str = ""
    top_topics: list[str] = field(default_factory=list)
    weak_formats: list[str] = field(default_factory=list)
    suggested_themes: list[str] = field(default_factory=list)


class AnalyticsAgent:
    def summarize(self, metrics: list[dict[str, object]]) -> AnalyticsSummary:
        raise NotImplementedError("Add analytics logic once metrics are available.")
