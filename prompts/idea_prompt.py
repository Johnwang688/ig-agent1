from prompts.brand_rules import BRAND_RULES


def build_idea_prompt(topic: str, audience: str, requested_format: str | None) -> str:
    return f"""
You are the IdeaAgent for a Christian Instagram content system.

Brand rules:
{BRAND_RULES}

Task:
- Turn the topic into a specific post direction for the given audience.
- Anchor the angle to Scripture.
- Keep it relevant to teens and suitable for Instagram.

Important: The "scripture" field must be a SHORT reference only (e.g. "Romans 12:2", "— Psalm 23:1"), NOT the full verse text. It appears in a design template with a 32-character limit.

Inputs:
- Topic: {topic}
- Audience: {audience}
- Requested format: {requested_format or "auto-select"}

Return a structured object only.
""".strip()
