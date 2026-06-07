# Proposal: Ensure Agent Skills Follow Standards

**Change Slug:** `01-ensure-agent-skills-follow-standards`  
**Author:** Product Owner Agent  
**Date:** 2026-05-16  
**Status:** Draft (awaiting @ralphke review)  
**Priority:** P1

---

## Intent

Skill definitions in `.github/skills/` and persona definitions in `.github/agents/` (also referred to in feedback as `.agents`) should be consistent with Agent Skills specification guidance and aligned with practical quality patterns referenced by Awesome Copilot. This proposal defines a review-first change so implementation work starts only after @ralphke approves the plan and done criteria.

## Scope

- Evaluate existing skill files in `.github/skills/` against agentskills.io specification and best-practice guidance.
- Targeted skills in scope: `idea-to-spec.md`, `spec-to-design.md`, `test-generation.md`, `security-review.md`, `pr-review.md`, `deploy-pipeline.md`.
- Evaluate persona files in `.github/agents/` for the same standard layout expectations (front matter + role, responsibilities, behavior rules, process/checklist, handoff protocol).
- Targeted personas in scope: all files in `.github/agents/*.md`.
- Update skill descriptions and structure to improve clarity, actionability, and optimization quality.
- Keep scope focused on `.github` skill-related assets plus supporting `scripts/` and `test/` artifacts for measurable evaluation.
- Define baseline vs post-change evaluation and summary reporting.

## Out of Scope

- Unrelated repository content outside skill-quality alignment.
- New runtime stacks beyond the issue constraints and existing tooling.
- Direct production feature implementation not related to skill quality.

## Approach

Create a standards checklist mapped to agentskills.io references, then apply targeted edits to skill documents. Add reusable evaluation scripts in `scripts/` and corresponding tests in `test/` to compare baseline prompts (without skills) against improved prompts (with updated skills). Implementation is blocked until this proposal is reviewed and accepted by @ralphke.

### Standards Snapshot (local checklist source)

- Required structure per skill: purpose, trigger/when-to-use, ordered execution steps, quality checks, and expected output.
- Description quality goals: concise intent, explicit scope boundaries, concrete actions, and low-ambiguity wording.
- Optimization goals: reduce vague phrasing, tighten stage handoffs, and improve consistency with repository SDLC labels.
- External references remain authoritative, but this snapshot is the minimum local rubric if external links are unavailable.

## Scenarios

### Scenario: Review-first planning gate
- GIVEN this issue requests a spec before execution
- WHEN this change is proposed
- THEN planning artifacts are created under `spec/openspec/changes/01-ensure-agent-skills-follow-standards/`
- AND no implementation task is started before @ralphke approval

### Scenario: Skill standards alignment
- GIVEN a skill file in `.github/skills/`
- WHEN it is updated for this change
- THEN it follows the required specification and best-practice guidance
- AND it remains compatible with repository SDLC persona flow

### Scenario: Persona layout consistency
- GIVEN persona files in `.github/agents/`
- WHEN they are reviewed in this change
- THEN each persona follows the same standard layout sections
- AND persona instructions remain aligned with the corresponding skill expectations

### Scenario: Measured quality improvement
- GIVEN baseline prompt evaluations without skill assistance
- WHEN post-change evaluations run with updated skills
- THEN the summary reports measurable improvement
- AND targeted metrics meet a relative improvement goal of at least 5% where measurable

## Acceptance Criteria

- [ ] All in-scope skills (`idea-to-spec`, `spec-to-design`, `test-generation`, `security-review`, `pr-review`, `deploy-pipeline`) follow best practices from https://agentskills.io/skill-creation/best-practices.
- [ ] All in-scope skills apply optimization guidance from https://agentskills.io/skill-creation/optimizing-descriptions.
- [ ] All in-scope persona files in `.github/agents/` follow a consistent standard layout and align with skill-stage handoffs.
- [ ] Validation shows measurable quality improvements against baseline without skills using defined metrics (instruction completeness, ambiguity reduction, and checklist coverage).
- [ ] Reusable script code is placed in `scripts/` using the allowed tooling priorities.
- [ ] Evaluation tests are placed in `test/` and demonstrate at least 5% relative improvement where measurable.
- [ ] @ralphke approves this proposal before implementation tasks are executed.
