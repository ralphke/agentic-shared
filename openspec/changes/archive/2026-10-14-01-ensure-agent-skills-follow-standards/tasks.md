# Tasks: Ensure Agent Skills Follow Standards

**Change Slug:** `01-ensure-agent-skills-follow-standards`  
**Status:** Complete  
**Date:** 2026-10-14

---

## Phase 0 — Review Gate

- [x] T01 — Confirm `proposal.md` is reviewed and approved before editing any
      `.github` agent-skill assets.

## Phase 1 — Define the Standard

- [x] T02 — Inventory all files in `.github/skills/` and `.github/agents/` to
      identify the current structure and variants to normalize.
- [x] T03 — Define the canonical standard for skill files: required sections,
      purpose, trigger/when-to-use, execution steps, quality checks, and
      expected output.
- [x] T04 — Define the canonical standard for persona files: role,
      responsibilities, behavior rules, stage handoff, and outputs, matching the
      repo’s Software Fabric flow.

## Phase 2 — Apply the Standard

- [x] T05 — Update the in-scope skill files in `.github/skills/` to match the
      approved skill standard, without expanding beyond the standards-only
      scope.
- [x] T06 — Update the in-scope persona files in `.github/agents/` to match the
      approved persona standard, preserving stage ownership and handoff
      behavior.
- [x] T07 — Apply only the minimal supporting updates needed in `.github/` to
      keep task flow, handoffs, and guidance consistent with the standard.

## Phase 3 — Validation

- [x] T08 — Run the repository’s relevant validation checks, capture a
      lightweight baseline-vs-improvement review for representative
      skill/persona files, and verify the updated agent assets remain
      structurally consistent and aligned with the SDLC model.
- [x] T09 — Confirm every acceptance criterion in `proposal.md` is satisfied for
      the narrowed standards-only scope, including the recorded
      baseline-vs-improvement validation evidence before closing the change.

## Execution Order Requirements

1. `T02` must run before `T03` and `T04`.
2. `T03` and `T04` must complete before `T05` and `T06`.
3. `T05` and `T06` must complete before `T07`.
4. `T07` must complete before `T08`.
5. `T08` must complete before `T09`.

## Scope Guardrails

- Do not create new runtime features, services, or product functionality.
- Do not add evaluation scripts, benchmark tooling, or measurement
  infrastructure unless explicitly added by a new change request.
- Keep all edits limited to the agent skills and persona governance artifacts
  required by this change.
