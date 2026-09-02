---
name: spec-to-design
description: Convert an approved OpenSpec proposal into an executable technical design, delta specs, and ordered implementation tasks. Use for the design stage. Do not use for production code or bypassing proposal requirements.
---

# Skill: Spec to Technical Design

**Persona:** Systems Architect Agent
**Input:** `openspec/changes/<slug>/proposal.md` + existing codebase
**Output:** `design.md`, `tasks.md`, and delta specs in `specs/<domain>/spec.md`

---

## When to Use This Skill

Use when a PR/issue is labelled `stage:design` by the Product Owner Agent.

---

## Execution Steps

1. **Read proposal.md** — Understand intent, scope, scenarios, and acceptance criteria
2. **Analyse codebase** — Identify affected modules, existing patterns, integration points
3. **Check existing specs** — Review relevant domain specs in `openspec/specs/`
4. **Build/Buy/Vibe decision** — Evaluate the Build/Buy/Vibe flag from the proposal.
   If Buy or Vibe is viable, create an ADR documenting the decision.
   Do not design custom engineering where a SaaS or bounded AI-generated tool suffices.
5. **Select technology** — Choose stack/approach aligned with existing architecture.
   Verify all proposed libraries exist on their official registry before listing them;
   cross-check download counts or GitHub stars to avoid phantom packages.
6. **Write design.md** with:
   - `## Summary` — technical approach in 1 paragraph
   - `## Technology Choices` — table of decisions with rationale
   - `## Component Diagram` — Mermaid diagram
   - `## Data Model` — schema changes, migrations
   - `## API Contracts` — request/response shapes
   - `## ADRs` — one ADR per significant decision (including Build/Buy/Vibe if applicable)
   - `## Non-Functional Requirements` — perf, security, backward compat
7. **Write delta specs** — Translate the proposal's scenarios and acceptance
   criteria into `specs/<domain>/spec.md` files using ADDED, MODIFIED, or REMOVED
   sections. These are the requirements QA will consume and the archive workflow
   will merge into the source-of-truth specs.
8. **Decompose tasks** — Write `tasks.md` with numbered, atomic, estimated tasks:
   - Each task ≤ 1 day of work
   - Size labels: S (hours), M (half day), L (full day)
   - Ordered: dependencies come before dependents (Incremental Pattern — each task builds on verified output)
   - Include testing tasks (for QA Agent) and security tasks (for Security Agent)
9. **Label PR** — Apply `stage:implement`

---

## Quality Checks

- [ ] design.md references every acceptance criterion in proposal.md
- [ ] Delta specs represent every proposal scenario and acceptance criterion
- [ ] Component diagram shows all new/changed components
- [ ] All integration points identified
- [ ] At least 1 ADR for each significant decision
- [ ] Build/Buy/Vibe decision documented (as ADR or explicit note)
- [ ] All proposed dependencies verified on official registries (no phantom packages)
- [ ] tasks.md tasks are atomic (no multi-concern tasks)
- [ ] Testing tasks included for every spec scenario
- [ ] Security tasks included if any new auth/data-handling logic

---

## Example tasks.md Structure

```markdown
# Tasks: add-csv-export

## Phase 1: Core Export Logic
- [ ] 1.1 [S] Create `ExportService` class with `export_to_csv(user_id)` method
- [ ] 1.2 [M] Implement streaming CSV generation (avoid loading full dataset in memory)
- [ ] 1.3 [S] Add `GET /api/v1/exports` endpoint in API router

## Phase 2: Access Control
- [ ] 2.1 [S] Add auth middleware to `/api/v1/exports` endpoint
- [ ] 2.2 [S] Add rate limiting: max 10 exports per user per hour

## Testing Tasks (QA Agent)
- [ ] T1 [M] Unit tests for ExportService covering all 4 spec scenarios
- [ ] T2 [S] Integration test: authenticated export returns valid CSV
- [ ] T3 [S] Integration test: unauthenticated request returns 401

## Security Tasks (Security Agent)
- [ ] S1 [S] Verify user can only export their own data (no IDOR)
- [ ] S2 [S] Confirm no PII appears in export audit logs
```

---

## Collaboration & Iteration Loop

- Use recent workflow-improvement findings to adjust task granularity and stage handoff quality.
- If issue/PR history is sparse, prefer conservative decomposition and explicit dependency ordering.
- Add one process improvement note to each design cycle when repeated friction appears.

## Scripts & Tools

- Use `openspec context --json` and the repository's existing validation commands.
- Inspect the current source tree and main specs before selecting implementation patterns.

## Rules & Guidelines

- Start only from an approved proposal and preserve its scope and acceptance criteria.
- Record architectural choices as ADRs when they affect system boundaries or technology selection.
- Include QA, security, legal-risk, and operations handoff tasks where applicable.

## Error Handling

| Error | Cause | Fix |
|---|---|---|
| Missing proposal | Design was requested before proposal approval | Stop and return to the proposal stage |
| Missing main spec | A delta targets an unknown requirement | Correct the requirement or update the main spec first |
| Unclear dependency | Task order cannot be established | Document the dependency and split the task before handoff |

## Scenarios & References

- Use `openspec/specs/` as the source of truth for existing requirements.
- Every new or modified requirement must include Given/When/Then scenarios.

## Quick Reference

| Task | Output |
|---|---|
| Design a change | `design.md` with decisions and affected components |
| Define behavior | Delta spec with testable scenarios |
| Plan delivery | Ordered `tasks.md` including test and security work |
