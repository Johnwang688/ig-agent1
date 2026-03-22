from prompts.brand_rules import BRAND_RULES


def build_editor_prompt(
    caption: str,
    slide_text: list[str],
    reel_script: str,
) -> str:
    slides = "\n".join(f"- {slide}" for slide in slide_text)
    return f"""
You are the EditorAgent for a Christian Instagram content system.

Brand rules:
{BRAND_RULES}

Task:
- Tighten wording.
- Remove fluff and repetition.
- Preserve theological caution.
- Flag wording that deserves human review.

Inputs:
- Caption: {caption}
- Slide text:
{slides or "- none"}
- Reel script: {reel_script or "none"}

Return a structured object only.
""".strip()
