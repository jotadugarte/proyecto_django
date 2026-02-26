# AI Developer Protocol & Refactoring Playbook

**Goal:** Replicate the "Deep Clean" process used across software projects to eliminate fragmentation, redundancy, and drift in documentation, and to optimize AI Agent workflows for the specific tech stack.

**Instruction to AI:** Execute this playbook phase by phase. Do not skip to solutions; perform the analysis first.

---

## Phase 1: Discovery & Inventory

**Goal:** Understand what we have.

1.  **List & Group:** List all files in `docs/` and group them by "Domain" (e.g., UI, Backend, Process, Legacy).
2.  **Roadmap Check:** If `docs/ROADMAP.md` exists, use it to compare planned vs implemented items during the Discovery phase.
3.  **Identify "Split Brains":** finding multiple documents that seem to cover the same topic (e.g., `ui_plan.md` and `ui_rebuild.md`, or `auth_flow_v1.md` and `AUTHENTICATION.md`).
4.  **Identify "Snapshots":** Find documents that look like point-in-time audits or specific task plans (e.g., `CODE_REVIEW_7df209c.md`, `feature_xyz_notes.md`) rather than living documentation.

## Phase 2: Redundancy Analysis (The "Dry" Check)

**Goal:** Find repeated information.

1.  **Cursorrules Check:** Compare `docs/` against `.cursorrules` and `docs/core/SYSTEM_ARCHITECTURE.md`.
    - _Question:_ Does any doc (e.g. a legacy `docs/tech_stack.md` or `docs/component_library.md`) merely duplicate `.cursorrules` or `docs/core/SYSTEM_ARCHITECTURE.md`?
2.  **Cross-Doc Check:** Do disparate docs repeat the same architectural patterns?

## Phase 3: Drift Analysis (Truth vs. Reality)

**Goal:** Ensure docs match the code.

1.  **Spec Audit:** Compare `docs/core/SPEC.md` against the core data layer (e.g., `app/models/`, `db/schema.ts`, `prisma/schema.prisma`). Are there models missing from the Spec? Are there relationships described in Spec that don't exist?
2.  **UI Audit:** Compare UI docs (if any) against the frontend components directory (e.g., `app/components/`, `src/views/`).

## Artifact Strategy (The "Wisdom" of Execution)

**Key Lesson:** The analysis phase generates meaningful artifacts (Inventory, Redundancy Analysis, Drift Analysis). These become "stale" the moment you execute fixes, but they are valuable audit logs.

- **Create** these artifacts in a temporary location or root `docs/` during analysis.
- **Move** them to `docs/audit/` with a descriptive date stamp (e.g., `YYYY-MM-DD_AI_AUDIT_PHASE_1_INVENTORY.md`) upon completion.

## Phase 4: Reconciliation (The Fix)

**Goal:** Resolve the drifts identified in Phase 3 while future-proofing the documentation.

1.  **Code vs. Spec Decision:** For each drift, decide: _Is the Code wrong, or is the Spec wrong?_ (Ask the user).
2.  **Execute Fix:** Update the code or the spec accordingly.
3.  **Add a Domain Glossary:** Add a strict terminology glossary to `SPEC.md`. This prevents AI from hallucinating standard industry definitions when the project uses specific internal terminology.
4.  **Deep-Link Feature Specs from Core:** Explicitly link feature-specific documents from the core `SPEC.md` using markdown links (e.g., `> **Implementation Deep Dive:** See [docs/features/FEATURE_NAME.md]`). This teaches the AI exactly where to look next.

## Phase 5: Consolidation & Cleanup

**Goal:** Execute the proposal from Phase 2 and optimize document storage.

1.  **Organize `docs/` Hierarchy:**
    - Group documents into logical subdirectories (e.g., `core/`, `features/`, `ai/`, `audit/`) so AI agents can be targeted to specific folders without polluting their context window.
2.  **Merge Split Brains:**
    - Read the source file (e.g., `obsolete_auth.md`).
    - Append its relevant content to the target file (e.g., `AUTH_SPEC.md`).
    - Delete the source file.
3.  **Archive Snapshots:** Move point-in-time docs to `docs/audit/` with a date prefix.
4.  **Final Sweep:** Move the analysis artifacts (Inventory, Redundancy, Drift reports) to `docs/audit/` with date prefixes.

## Phase 6: AI Agent & Workflow Optimization

**Goal:** Ensure AI assistants operate as strict state machines with persistent memory and adherence to the AgentCore architecture.

1.  **Agent OS Initialization:**
    - Ensure `.agentcore/` directory exists with `current_state.md`, `blocker_log.md`, and `pending_refactors.md`.
    - Ensure `docs/ROADMAP.md` exists (AgentCore sync initializes it) for project planning and task tracking.
    - Consolidate AI rules into `.cursorrules` to act as an IF/THEN routing table, and ensure it contains the `<agentcore_operating_system>` header.
    - **CRITICAL RULE:** All agents and instructions must explicitly forbid auto-committing or auto-pushing code. At most, suggest a commit message.
    - Delete legacy directories (e.g. `.agent/`, `.cursor/rules/`) if they duplicate `.agentcore/` or `.cursorrules`; ensure all tools share a single source of truth.
2.  **Skill Refinement (XML State Machines):**
    - Update universal workflow skills (e.g., `start-task`, `finish-branch`, `status-check`) to ensure they use strict `<agentcore_skill>` XML formatting.
    - **Start Task:** Ensure the AI forces a classification phase, drafts a hierarchical implementation plan inside the active session file (`active_sessions/task_*.md`), checks `SYSTEM_ARCHITECTURE.md`, and loops through strict TDD.
    - **Finish Branch:** Ensure the AI handles async loops (like waiting for remote bots) by pausing and yielding control.
    - **Status Check:** Ensure the skill can rehydrate context by reading `.agentcore/current_state.md` and the implementation plan inside the active session file to pinpoint blockers.
3.  **Playbook Documentation:**
    - Ensure `docs/ai/AI_WORKFLOW_PLAYBOOK.md` exists to document the exact purpose and triggers for all Custom Skills and the Memory architecture.
4.  **Prevent Future "Drift" via PR Templates:**
    - Add required checkboxes to `.github/PULL_REQUEST_TEMPLATE.md` forcing developers to attest they have updated `SPEC.md` (if schema changes) or `SYSTEM_ARCHITECTURE.md` (if the stack changes).
