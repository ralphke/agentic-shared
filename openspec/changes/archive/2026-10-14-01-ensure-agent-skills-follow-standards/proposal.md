# Proposal: Ensure Agent Skills Follow Standards

**Change Slug:** `01-ensure-agent-skills-follow-standards`  
**Author:** Product Owner Agent  
**Date:** 2026-05-16  
**Status:** Draft (awaiting @ralphke review)  
**Priority:** P1

---

## Intent

This change standardizes the repository’s agent skill and persona definitions so they follow a consistent structure, align with the project’s Software Fabric stage model, and remain clear, actionable, and easy to maintain. The goal is governance and quality control for shared agent assets, not runtime feature development.

## Scope

- Review existing skill files in `.github/skills/` for structural consistency and clarity.
- Review persona files in `.github/agents/` for a consistent layout and predictable handoff behavior.
- Align skill/persona definitions with the project’s intended SDLC flow, including stage ownership, responsibilities, and handoff expectations.
- Update only the shared agent asset definitions needed to enforce the standard.
- Keep the change focused on repository standards and documentation quality.

## Out of Scope

- New runtime features or system behavior outside agent asset governance.
- Broad workflow redesign beyond the skill/persona standard.
- Supporting evaluation scripts, benchmark tooling, or repo-wide measurement infrastructure.
- Implementation work unrelated to the standardization of agent skill/persona content.

## Approach

Define a concise repository standard for agent skill and persona files, then apply that standard to the relevant assets in `.github/skills/` and `.github/agents/`. The standard will emphasize:

- clear purpose and when-to-use guidance
- explicit responsibilities and behavior rules
- predictable handoff protocol and stage ownership
- consistent structure across agent assets
- reduced ambiguity in wording and execution guidance

### Standards Snapshot (local rubric)

- Required structure for skills: purpose, trigger, execution steps, quality checks, and expected output.
- Required structure for personas: role, responsibilities, behavior rules, workflow expectations, and handoff protocol.
- Description quality goals: concise intent, clear boundaries, actionable wording, and low ambiguity.
- Alignment goals: keep persona guidance consistent with the repository’s Software Fabric stage model and agent roster.
- Validation goal: capture a lightweight baseline-vs-improvement review using a small representative rubric for a few agent assets, without introducing broad benchmark tooling or evaluation infrastructure.

## Scenarios

### Scenario: Skill structure consistency
- GIVEN a skill file in `.github/skills/`
- WHEN it is reviewed for this change
- THEN it follows the repository’s required structure and purpose-driven guidance
- AND it remains aligned with the project’s SDLC roles and stage flow

### Scenario: Persona layout consistency
- GIVEN a persona file in `.github/agents/`
- WHEN it is reviewed for this change
- THEN it uses a consistent section layout and clear handoff rules
- AND its responsibilities, triggers, and outputs are understandable to the next stage owner

### Scenario: Standards-only review gate
- GIVEN this change updates shared agent standards
- WHEN the proposal is reviewed
- THEN implementation stays limited to documentation and definition updates
- AND no product functionality or unrelated workflow changes are introduced

## Acceptance Criteria

- [ ] All in-scope skill files in `.github/skills/` follow a consistent repository standard.
- [ ] All in-scope persona files in `.github/agents/` follow a consistent layout and handoff structure.
- [ ] Skill and persona guidance remain aligned with the Software Fabric stage model and repository conventions.
- [ ] Updated definitions remove avoidable ambiguity and improve clarity of execution expectations.
- [ ] A lightweight baseline-vs-improvement validation record is captured for representative agent assets, without introducing broad benchmark tooling or evaluation infrastructure.
- [ ] The change remains limited to agent asset standards and governance; no unrelated feature work is introduced.
- [ ] The proposal is reviewed before implementation work proceeds beyond the planned standardization scope.
