# Engineering Design Document

## Project
AI-Assisted Christian Instagram Content Pipeline

## Executive Summary
This system is a human-in-the-loop content production pipeline for a Christian Instagram page aimed at conservative teens. AI agents generate topic angles, draft copy, refine tone, select visual direction, choose reusable templates, and prepare structured inputs for final asset rendering. A human must review and approve every post before scheduling or publishing.

The recommended v1 stack is:

- OpenAI Responses API for language agents and structured outputs
- Placid for deterministic template-based image rendering
- SQLite for low-friction local persistence
- A local CLI prototype before building a dashboard

This architecture prioritizes theological consistency, brand quality, repeatability, and operator control over full automation.

## Problem Statement
The system must help an operator run a Christian Instagram page with:

- Consistent theological framing
- Repeatable visual quality
- Faster content throughput
- Human review before publishing
- Low dependence on expensive or enterprise-only design tooling

The pipeline must produce final visual assets for Instagram posts, carousels, and Reel covers, not only text drafts.

## Goals
- Generate post concepts aligned to the brand and audience
- Draft captions, carousel slides, hooks, titles, and optional Reel scripts
- Enforce brand voice and theological guardrails
- Select a matching visual direction for each post
- Fill reusable design templates with structured content
- Require explicit human approval before scheduling
- Keep the first implementation simple and inexpensive

## Non-Goals
- Fully autonomous posting without human review
- Freeform AI poster generation with rendered text in image models
- Crisis counseling or high-stakes spiritual advice
- Deep comment moderation in v1
- Full video editing automation in v1

## Why This Architecture
The design deliberately separates reasoning, copy generation, editorial cleanup, visual direction, template selection, and rendering.

This split reduces failure modes:

- Language agents focus on ideas and copy, not design rendering
- Template routing stays separate from rendering logic
- Template-based rendering preserves readability and consistency
- A hard approval gate prevents accidental publishing

Placid is a better default renderer for v1 than Canva because Placid supports direct template-based rendering through structured API inputs, while Canva Autofill requires a Canva Enterprise organization and delegated user access.

## System Context
The operator provides a topic or weekly theme list. The system transforms that into draft content, rendered image assets, and approval-ready records. Approved posts are then eligible for scheduling and later analytics review.

## High-Level Architecture
```text
Operator
  -> Content Request
  -> IdeaAgent
  -> WriterAgent
  -> EditorAgent
  -> CreativeDirectionAgent
  -> TemplateFinderAgent
  -> TemplateRenderAgent
  -> Human Approval Gate
  -> Scheduler / Publisher
  -> AnalyticsAgent
```

## Core Design Principles
- No post may be scheduled or published without explicit human approval
- AI outputs should be structured wherever downstream systems depend on typed fields
- Rendering must use approved templates rather than freeform text-in-image generation
- Renderer-specific implementation details should stay behind a service interface
- Prompting rules and brand rules must be versioned assets

## Functional Requirements
### Content Generation
- Accept a topic, audience, and requested format
- Generate a specific angle anchored to Scripture
- Produce copy tailored to carousels, Reels, or quote-style posts
- Edit for clarity, brevity, and tone consistency

### Visual Production
- Turn the approved copy draft into a visual direction
- Select from an approved template catalog only
- Render final assets with structured layer data
- Return a review-ready asset URL and render metadata

### Review and Scheduling
- Allow an operator to approve or reject posts
- Store review notes and revision requests
- Prevent scheduling when `approved_by_human` is false
- Preserve an audit trail for approval and scheduling events

### Analytics
- Track topics, formats, and output metadata
- Summarize performance and suggest future content directions

## Non-Functional Requirements
- Deterministic rendering for reusable designs
- Low operational complexity in v1
- Easy local development and testing
- Extensibility for future renderers and schedulers
- Traceable prompts, outputs, template usage, and approvals

## Agent Catalog
### IdeaAgent
Purpose: Turn a raw topic into a clear, teen-relevant post direction.

Inputs:
- Topic
- Audience
- Brand rules
- Requested format or default format

Outputs:
- Angle
- Scripture reference
- Hook
- Title
- Suggested format

Responsibilities:
- Identify a relevant angle for teens
- Anchor the idea in Scripture
- Avoid repetitive or generic framing

### WriterAgent
Purpose: Produce first-draft content for the selected format.

Inputs:
- Angle
- Scripture
- Hook
- Title
- Format
- Brand rules
- Template constraints when available

Outputs vary by format:
- Caption
- Slide text
- Reel script
- CTA
- Hashtags

Responsibilities:
- Produce concise Instagram-native copy
- Speak directly to teens
- Respect text limits for target templates

### EditorAgent
Purpose: Refine draft copy for consistency, clarity, and brevity.

Inputs:
- Draft copy
- Brand rules
- Theological guardrails

Outputs:
- Edited caption
- Edited slide text
- Edited Reel script
- Risk flags or review notes

Responsibilities:
- Tighten weak openings
- Remove fluff and repetition
- Normalize tone
- Flag wording that needs human review

### CreativeDirectionAgent
Purpose: Translate copy into a visual concept that fits the brand and template system.

Inputs:
- Final draft text
- Selected format
- Brand aesthetic settings

Outputs:
- Visual style
- Mood
- Palette
- Composition guidance
- Preferred template family
- Recommended background type

Responsibilities:
- Preserve brand consistency
- Avoid visual cliches
- Favor readability on Instagram

### TemplateFinderAgent
Purpose: Select the best reusable template from an approved catalog.

Inputs:
- Format
- Visual style
- Content density
- Template catalog

Outputs:
- Renderer vendor
- Template ID
- Field map ID

Responsibilities:
- Route to approved templates only
- Match content density to template limits
- Keep the feed visually consistent

### TemplateRenderAgent
Purpose: Render final assets from structured template inputs.

Primary implementation:
- Placid REST API

Inputs:
- Template ID
- Field values
- Optional background image URL
- Output dimensions

Outputs:
- Render job ID
- Status
- Final image URL
- Render metadata

Responsibilities:
- Map semantic fields into renderer-specific layer names
- Submit render jobs
- Poll for completion
- Attach the final asset URL to the post record

### Approval Gate
Purpose: Block publication unless a human explicitly approves the post.

Inputs:
- Completed post record
- Rendered asset
- Operator decision

Outputs:
- Approved or rejected status
- Review notes

Responsibilities:
- Enforce manual approval
- Preserve revision notes
- Route rejected posts back into revision

### SchedulerAgent
Purpose: Queue approved posts for publication.

Inputs:
- Approved post
- Scheduled timestamp
- Platform metadata

Outputs:
- Scheduled status
- Platform scheduling ID

Responsibilities:
- Schedule approved content only
- Maintain an audit trail
- Handle retries and external failures

### AnalyticsAgent
Purpose: Close the feedback loop using post performance data.

Inputs:
- Post metrics
- Post metadata
- Topic and format history

Outputs:
- Weekly summary
- Top-performing topics
- Weak-performing formats
- Suggested future themes

Responsibilities:
- Identify patterns
- Reduce repeated content
- Improve future topic and format choices

## Data Model
### Core Post Object
The `Post` model should track:

- Request metadata such as topic, audience, and format
- Idea-stage outputs such as angle, scripture, hook, and title
- Copy outputs such as caption, slides, Reel script, CTA, and hashtags
- Creative direction fields such as style, palette, and composition
- Template and renderer metadata
- Approval, scheduling, and audit state

### Template Metadata
Each reusable template definition should include:

- Template ID
- Renderer
- Format
- Style family
- Character budgets for relevant fields
- Layer-name mappings for semantic fields

Template metadata is required because different templates have different field names and text capacity.

## State Model
Recommended `Post.status` values:

- `idea`
- `drafted`
- `edited`
- `art_directed`
- `template_selected`
- `rendered`
- `in_review`
- `approved`
- `rejected`
- `scheduled`
- `published`
- `failed`

Transitions should be explicit and validated by the pipeline.

## Services Layer
### OpenAI Service
Responsibilities:
- Wrap the Responses API behind a typed interface
- Expose `generate_structured()` and `generate_text()`
- Centralize model choice, retries, and logging

### Template Renderer Service
Responsibilities:
- Hide Placid-specific implementation details
- Support rendering, status checks, and final URL resolution

### Approval Store
Responsibilities:
- Persist review state and operator notes
- Track revisions and approval decisions

### Scheduler Service
Responsibilities:
- Abstract publishing or scheduling providers
- Enforce the approval prerequisite

## Prompt and Rules System
### Brand Rules
Brand rules are the most important static asset in the system. They should define:

- Audience
- Tone
- Theological constraints
- Banned phrasing
- Allowed themes
- Style guidance
- Length guidance

### Prompt Assets
Each agent should receive:

- System rules
- Task instructions
- Schema requirements
- Context blocks
- Examples when needed

Prompts should be versioned as separate files, not buried in code.

## Template Strategy
### Why Templates
Templates provide:

- Feed consistency
- Readable typography
- Faster production
- Lower rendering risk

### Initial Approved Template Inventory
- Quote post
- Verse encouragement
- Carousel title slide
- Teaching carousel body
- Reel cover

### Field Maps
Each template should have a fixed semantic-to-layer mapping such as:

- `title -> headline_layer`
- `subtitle -> subhead_layer`
- `verse -> verse_layer`
- `cta -> footer_layer`

Avoid universal dynamic mapping in v1.

## End-to-End Workflow
### Generation Phase
1. Operator submits a topic or weekly theme list.
2. IdeaAgent creates one or more directions.
3. WriterAgent drafts copy.
4. EditorAgent refines the draft.
5. CreativeDirectionAgent defines the visual direction.
6. TemplateFinderAgent selects an approved template.
7. TemplateRenderAgent renders the final asset.

### Review Phase
1. Operator reviews the content and rendered asset.
2. Operator approves or rejects the post.
3. Rejected posts return to a revision queue with notes.

### Publish Phase
1. Scheduler service queues approved posts only.
2. The post is published through an adapter.
3. Metrics flow into analytics processing.

## Implementation Plan
### Phase 1: Local Prototype
- Single Python project
- CLI runner
- Local SQLite or JSON storage
- One OpenAI wrapper
- One Placid renderer
- Human review in terminal
- No automatic publishing yet

### Phase 2: Internal Tool
- Simple web dashboard
- Approval queue
- Template inventory browser
- Revision comments
- Scheduling integration

### Phase 3: Optimization
- Weekly batch planning
- Analytics-guided topic selection
- Asset library support
- Background image selection
- Hook testing and experimentation

## Recommended Code Structure
```text
project/
├── app.py
├── config/
│   └── settings.py
├── models/
│   ├── post.py
│   └── template.py
├── schemas/
│   ├── idea_schema.py
│   ├── writer_schema.py
│   ├── editor_schema.py
│   └── creative_schema.py
├── prompts/
│   ├── brand_rules.py
│   ├── idea_prompt.py
│   ├── writer_prompt.py
│   ├── editor_prompt.py
│   └── creative_prompt.py
├── agents/
│   ├── idea_agent.py
│   ├── writer_agent.py
│   ├── editor_agent.py
│   ├── creative_direction_agent.py
│   ├── template_finder_agent.py
│   ├── template_render_agent.py
│   ├── approval_agent.py
│   └── analytics_agent.py
├── services/
│   ├── openai_service.py
│   ├── placid_service.py
│   ├── approval_store.py
│   └── scheduler_service.py
├── pipeline/
│   └── content_pipeline.py
└── data/
    ├── templates.json
    └── posts.db
```

## Key Implementation Details
### Structured Outputs
Every agent that returns objects should use structured outputs. This reduces brittle parsing and makes downstream orchestration more reliable.

### Template Rendering
Use explicitly named layers in Placid templates and store those mappings in configuration or template metadata.

### Approval Enforcement
Scheduling and publishing must raise an error when `approved_by_human` is false.

### Logging
Persist:

- Prompts
- Prompt versions
- Schema versions
- Agent outputs
- Selected template metadata
- Render job IDs
- Approval notes

## Risks and Mitigations
### Theological Drift
Mitigation:
- Strong brand rules
- Editorial review
- Mandatory human approval

### Generic or Repetitive Content
Mitigation:
- Topic history checks
- Analytics feedback loop

### Render Overflow
Mitigation:
- Per-template text budgets
- Pre-render validation

### Renderer Lock-In
Mitigation:
- Keep rendering behind a service interface

### Over-Automation
Mitigation:
- Preserve manual approval
- Allow human edits before scheduling

## Future Extensions
- Stock image selector agent
- Background image generation support
- Reel thumbnail generator
- Auto-caption export
- Review dashboard
- Slack or Telegram approvals
- Multi-account publishing
- Per-format performance optimization

## Final Recommendation
Build v1 with:

- OpenAI Responses API for text agents
- Structured outputs for typed agent responses
- Placid for template-based rendering
- SQLite or JSON persistence
- A strict human approval gate
- No automated publishing until content quality is stable

This provides the smallest useful system that solves the real workflow: AI accelerates drafting and assembly, while a human stays in control of theology, tone, and publication.
