from __future__ import annotations

import argparse

from agents.approval_agent import ApprovalAgent
from config.settings import Settings
from models.post import PostFormat, PostStatus
from runtime import build_runtime, create_post, load_templates, render_post_details


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="AI-Assisted Christian Instagram Content Pipeline"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate_parser = subparsers.add_parser("generate", help="Generate a new post draft")
    generate_parser.add_argument("--topic", required=True, help="Topic or content theme")
    generate_parser.add_argument(
        "--audience",
        default="Conservative Christian teens",
        help="Audience description",
    )
    generate_parser.add_argument(
        "--format",
        choices=[fmt.value for fmt in PostFormat],
        default=PostFormat.CAROUSEL.value,
        help="Requested Instagram format",
    )

    list_parser = subparsers.add_parser("list", help="List stored posts")
    list_parser.add_argument(
        "--status",
        choices=[status.value for status in PostStatus],
        help="Optional status filter",
    )

    review_parser = subparsers.add_parser("review", help="Review pending posts")
    review_parser.add_argument("--post-id", help="Specific post id to review")

    return parser


def handle_generate(args: argparse.Namespace, settings: Settings) -> None:
    runtime = build_runtime(settings)
    templates = load_templates(settings)
    post = create_post(args.topic, args.audience, args.format)
    result = runtime.pipeline.generate(post, templates)
    print("Generated post and submitted it for review.\n")
    print(render_post_details(result.post))


def handle_list(args: argparse.Namespace, settings: Settings) -> None:
    runtime = build_runtime(settings)
    status = PostStatus(args.status) if args.status else None
    posts = runtime.approval_store.list_posts(status=status)
    if not posts:
        print("No posts found.")
        return

    for post in posts:
        approved = "yes" if post.approved_by_human else "no"
        print(
            f"{post.id} | status={post.status.value} | format={post.format.value} "
            f"| approved={approved} | topic={post.topic}"
        )


def handle_review(args: argparse.Namespace, settings: Settings) -> None:
    runtime = build_runtime(settings)

    if args.post_id:
        post = runtime.approval_store.get_post(args.post_id)
        if post is None:
            print(f"Post not found: {args.post_id}")
            return
    else:
        pending_posts = runtime.approval_store.list_pending_review()
        if not pending_posts:
            print("No posts are waiting for review.")
            return

        print("Posts waiting for review:")
        for index, pending_post in enumerate(pending_posts, start=1):
            print(f"{index}. {pending_post.id} | {pending_post.topic}")
        selected = input("\nSelect a post number to review: ").strip()
        if not selected.isdigit():
            print("Invalid selection.")
            return
        selected_index = int(selected) - 1
        if selected_index < 0 or selected_index >= len(pending_posts):
            print("Selection out of range.")
            return
        post = pending_posts[selected_index]

    print(render_post_details(post))
    decision = input("\nApprove this post? [y/n]: ").strip().lower()
    if decision not in {"y", "n"}:
        print("Review cancelled.")
        return
    notes = input("Optional review notes: ").strip() or None

    approval_agent = ApprovalAgent(runtime.approval_store)
    updated_post = approval_agent.review(post, approved=decision == "y", notes=notes)
    print(f"\nReview saved. New status: {updated_post.status.value}")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    settings = Settings.from_env()

    if args.command == "generate":
        handle_generate(args, settings)
    elif args.command == "list":
        handle_list(args, settings)
    elif args.command == "review":
        handle_review(args, settings)


if __name__ == "__main__":
    main()
