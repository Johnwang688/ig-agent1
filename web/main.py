from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from agents.approval_agent import ApprovalAgent
from config.settings import Settings
from models.post import PostFormat, PostStatus
from runtime import build_runtime, create_post, fetch_templates
from services.openai_service import OpenAIServiceError
from services.placid_service import PlacidServiceError


BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "web" / "templates"))

settings = Settings.from_env()
runtime = build_runtime(settings)

app = FastAPI(title="Christian Instagram Content Pipeline")


def home_context(error_message: str | None = None) -> dict[str, object]:
    posts = runtime.approval_store.list_posts()
    templates, template_errors = fetch_templates(settings)
    return {
        "counts": {
            "total": len(posts),
            "in_review": sum(post.status == PostStatus.IN_REVIEW for post in posts),
            "approved": sum(post.status == PostStatus.APPROVED for post in posts),
            "rejected": sum(post.status == PostStatus.REJECTED for post in posts),
        },
        "formats": [post_format.value for post_format in PostFormat],
        "templates": templates,
        "template_errors": template_errors,
        "default_audience": "Conservative Christian teens",
        "error_message": error_message,
    }


@app.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=home_context(),
    )


@app.post("/generate", response_model=None)
def generate_post(
    request: Request,
    topic: str = Form(...),
    audience: str = Form(...),
    format_name: str = Form(...),
    template_id: str = Form(""),
) -> Response:
    templates_list, _ = fetch_templates(settings)
    try:
        post = create_post(topic, audience, format_name)
        result = runtime.pipeline.generate(
            post,
            templates_list,
            selected_template_id=template_id or None,
        )
        return RedirectResponse(url=f"/posts/{result.post.id}", status_code=303)
    except (OpenAIServiceError, PlacidServiceError, ValueError) as exc:
        context = home_context(error_message=str(exc))
        context["default_audience"] = audience
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context=context,
            status_code=400,
        )


@app.get("/review-queue", response_class=HTMLResponse)
def review_queue(request: Request) -> HTMLResponse:
    posts = runtime.approval_store.list_pending_review()
    return templates.TemplateResponse(
        request=request,
        name="review_queue.html",
        context={"posts": posts},
    )


@app.get("/posts/{post_id}", response_class=HTMLResponse)
def post_detail(request: Request, post_id: str) -> HTMLResponse:
    post = runtime.approval_store.get_post(post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found.")

    return templates.TemplateResponse(
        request=request,
        name="post_detail.html",
        context={"post": post},
    )


@app.post("/posts/{post_id}/edit")
def edit_post(
    post_id: str,
    hook: str = Form(""),
    scripture: str = Form(""),
    angle: str = Form(""),
    caption: str = Form(""),
    cta: str = Form(""),
    reel_script: str = Form(""),
) -> RedirectResponse:
    post = runtime.approval_store.get_post(post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found.")

    post.hook = hook.strip() or None
    post.scripture = scripture.strip() or None
    post.angle = angle.strip() or None
    post.caption = caption.strip() or None
    post.cta = cta.strip() or None
    post.reel_script = reel_script.strip() or None
    runtime.approval_store.save_post(post)
    return RedirectResponse(url=f"/posts/{post_id}", status_code=303)


@app.post("/posts/{post_id}/edit-slides")
def edit_post_slides(
    post_id: str,
    slides: str = Form(""),
) -> RedirectResponse:
    post = runtime.approval_store.get_post(post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found.")

    post.slide_text = [s.strip() for s in slides.split("\n---\n") if s.strip()]
    runtime.approval_store.save_post(post)
    return RedirectResponse(url=f"/posts/{post_id}", status_code=303)


@app.post("/posts/{post_id}/edit-hashtags")
def edit_post_hashtags(
    post_id: str,
    hashtags: str = Form(""),
) -> RedirectResponse:
    post = runtime.approval_store.get_post(post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found.")

    post.hashtags = [h.strip() for h in hashtags.split() if h.strip()]
    runtime.approval_store.save_post(post)
    return RedirectResponse(url=f"/posts/{post_id}", status_code=303)


@app.post("/posts/{post_id}/review")
def review_post(
    post_id: str,
    decision: str = Form(...),
    review_notes: str = Form(""),
) -> RedirectResponse:
    post = runtime.approval_store.get_post(post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found.")

    approval_agent = ApprovalAgent(runtime.approval_store)
    approved = decision == "approve"
    approval_agent.review(post, approved=approved, notes=review_notes or None)
    return RedirectResponse(url=f"/posts/{post_id}", status_code=303)
