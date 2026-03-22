# Implementation Backlog

## Phase 1: Local Prototype
Goal: produce a working local pipeline that generates structured content, renders a template-based asset, and enforces human approval before scheduling.

### 1. Project Setup
- Create the Python package structure
- Add configuration loading for environment variables and local paths
- Add base models, schemas, prompts, and service interfaces
- Add seed data for template definitions

### 2. Core Domain Models
- Implement `Post` dataclass with lifecycle state fields
- Implement `TemplateDefinition` dataclass with text budgets and layer mappings
- Define enums or constants for post formats, renderers, and statuses
- Add simple serialization helpers for local persistence

### 3. Prompt and Rules Assets
- Write the brand rules asset
- Write prompt templates for Idea, Writer, Editor, and Creative Direction agents
- Version prompts so prompt changes are traceable
- Add example context blocks for schema-guided generation

### 4. OpenAI Integration
- Implement an `OpenAIService` interface
- Add a placeholder Responses API client wrapper
- Support `generate_text()` and `generate_structured()`
- Capture request metadata for debugging

### 5. Agent Implementations
- Implement `IdeaAgent` using structured outputs
- Implement `WriterAgent` for carousel, reel, and quote flows
- Implement `EditorAgent` for tone cleanup and risk flags
- Implement `CreativeDirectionAgent` for visual direction
- Implement `TemplateFinderAgent` for inventory-based template routing

### 6. Template Rendering
- Implement a renderer abstraction
- Add a Placid service implementation shell
- Add semantic field to layer-name mapping support
- Add pre-render validation for template text budgets

### 7. Storage and Approval
- Implement a local approval store using SQLite or JSON
- Add methods for saving drafts, reviews, and status transitions
- Implement approval and rejection operations with review notes
- Enforce `approved_by_human` before any scheduling action

### 8. Pipeline Orchestration
- Implement a `ContentPipeline` coordinator
- Add sequential steps from idea generation through render
- Add a revision path for rejected posts
- Add status transitions and failure handling

### 9. CLI Prototype
- Build a simple CLI entrypoint
- Allow the operator to submit a topic and format
- Print review-friendly post summaries
- Support approve, reject, and resubmit actions in terminal

### 10. Testing
- Add unit tests for model validation and state transitions
- Add tests for template fit validation
- Add tests for approval enforcement
- Add mock-based tests for OpenAI and Placid interfaces

## Phase 2: Internal Tool
Goal: replace the terminal workflow with a lightweight operator dashboard.

### 1. Dashboard Foundation
- Choose a lightweight web framework
- Add a list view for posts by status
- Add detail pages for content, prompts, and rendered assets
- Add authentication if the tool will be remotely accessible

### 2. Approval Queue
- Build an operator review queue
- Add approve, reject, and comment actions
- Surface revision history and prior versions
- Add filters by format, status, and date

### 3. Template Management
- Build a template inventory browser
- Expose field maps and text budgets
- Add template preview metadata
- Support enabling or disabling templates

### 4. Scheduling Integration
- Define a publisher adapter interface
- Add the first Instagram scheduling integration
- Persist external scheduling IDs and retry state
- Add basic scheduling logs

### 5. Workflow Usability
- Add revision assignments and notes
- Add draft duplication for similar posts
- Add batch theme creation for a week of content
- Add search by scripture, topic, or format

## Phase 3: Optimization
Goal: improve throughput, quality, and insight once the basic workflow is stable.

### 1. Analytics Loop
- Import post performance metrics
- Build weekly summaries
- Suggest future topics based on engagement trends
- Detect overused themes and weak formats

### 2. Creative Enhancements
- Add background image selection support
- Add optional stock asset libraries
- Add Reel thumbnail generation helpers
- Add A/B testing for hooks and cover text

### 3. Operational Improvements
- Add background job processing
- Add retry and dead-letter handling for failed renders
- Add prompt performance tracking
- Add audit exports for approvals and publishing history

## Cross-Cutting Tasks
- Keep prompts and schemas versioned
- Preserve audit logs for every important transition
- Maintain strict approval enforcement across all adapters
- Document environment variables and setup steps
- Keep renderer and publisher integrations behind interfaces

## Suggested First Sprint
- Scaffold the project structure
- Implement domain models and schemas
- Add prompt assets and brand rules
- Build the OpenAI and renderer service interfaces
- Implement a basic pipeline shell
- Create a terminal-based approval flow
