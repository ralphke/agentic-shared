# Tasks: Ensure Agent Skills Follow Standards

**Change Slug:** `01-ensure-agent-skills-follow-standards`  
**Status:** Planned  
**Date:** 2026-05-16

---

## Phase 0 — Review Gate

- [ ] T01 — Request and capture @ralphke review/approval of `proposal.md` before execution.

## Phase 1 — Standards Mapping

- [ ] T02 — Build a per-skill compliance checklist mapped to agentskills.io specification and best-practice sections.
- [ ] T03 — Build a per-persona layout checklist for `.github/agents/*.md` and map it to the same standard sections used by skills.
- [ ] T04 — Record baseline quality metrics for each targeted skill/persona using no-skill prompt evaluations.

## Phase 2 — Skill Improvements

- [ ] T05 — Update `.github/skills/*.md` files to align structure, intent clarity, and optimization guidance.
- [ ] T06 — Update `.github/agents/*.md` files where needed to enforce a consistent standard layout.
- [ ] T07 — Apply only necessary related updates in `.github` to keep persona/skill handoffs consistent.

## Phase 3 — Evaluation and Proof

- [ ] T08 — Add reusable evaluation scripts in `scripts/` using allowed tooling constraints.
- [ ] T09 — Add evaluation tests in `test/` and produce before/after summary output.
- [ ] T10 — Confirm measurable improvement and target at least 5% relative gain using these metrics: instruction completeness score, ambiguous-instruction count (inverse), and checklist coverage score.

## Phase 4 — Validation

- [ ] T11 — Run repository validation checks and attach evidence to the PR.
- [ ] T12 — Verify all acceptance criteria are checked before handoff.
