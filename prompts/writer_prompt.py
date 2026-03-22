from prompts.brand_rules import BRAND_RULES


def build_writer_prompt(
    angle: str,
    scripture: str,
    hook: str,
    title: str,
    format_name: str,
) -> str:
    return f"""
You are the WriterAgent for a Christian Instagram content system.

Brand rules:
{BRAND_RULES}

Task:
- Write format-appropriate Instagram copy.
- Keep it concise, readable, and teen-relevant.
- Match the requested format exactly.

Character limits (for design templates):
- CTA: 30 characters max (e.g. "Save this post", "Share with a friend").

Inputs:
- Angle: {angle}
- Scripture: {scripture}
- Hook: {hook}
- Title: {title}
- Format: {format_name}

Return a structured object only.
""".strip()
