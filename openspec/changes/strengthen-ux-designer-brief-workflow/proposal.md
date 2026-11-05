# Proposal

## Why

The UX Designer persona names important outcomes but does not yet give the
agent a consistent, evidence-grounded method for producing testable UX
requirements. A dedicated skill and focused persona updates will help the
Architect and QA turn the brief into an implementation-ready, verifiable
experience without inventing user needs or prescribing technology.

## What Changes

- Strengthen the UX Designer Agent's brief requirements to capture target
  users, goals, proposal evidence, assumptions, and unresolved questions.
- Require traceable, testable UX acceptance criteria and explicit coverage of
  applicable interaction states and accessibility checks.
- Add a dedicated UX design skill with an ordered brief-development workflow,
  quality checks, expected output, and guidance for missing or conflicting
  evidence.
- Keep the skill platform-neutral and preserve UX, architecture, and QA
  ownership boundaries.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `personas`: Strengthen the UX Designer Agent's brief contract and define its
  dedicated UX design skill, including evidence handling, testable criteria,
  state coverage, and accessibility quality checks.

## Scope

- Update `.github/agents/ux-designer.agent.md`.
- Add a dedicated skill under `.github/skills/` for producing UX briefs.
- Add focused validation for the agent/skill contract and record a lightweight
  baseline-versus-improved quality assessment.

## Out of Scope

- Producing application code, visual mockups, or framework-specific designs.
- Changing stage ownership, workflow gates, Architect technology decisions, or
  QA execution responsibilities.
- Requiring user research, usability testing, or device testing when no such
  evidence or environment is available.

## Acceptance Criteria

- The UX brief requires user goals and source evidence to be distinguished from
  assumptions and unknowns; gaps that affect requirements are returned for
  clarification rather than silently invented.
- UX acceptance criteria are actionable, verifiable, and traceable to proposal
  needs, and relevant interaction states are explicitly considered.
- Accessibility checks are applicable to the experience and specific enough
  for Architect and QA handoff, while preserving the WCAG 2.2 AA target.
- The new skill follows the shared skill standard and gives a repeatable,
  platform-neutral workflow with inputs, outputs, quality checks, and
  stop/clarification conditions.
- A representative before-and-after assessment records the change in clarity,
  structure, execution guidance, and handoff quality.

## Impact

- `.github/agents/ux-designer.agent.md`
- `.github/skills/ux-design/SKILL.md`
- `openspec/specs/personas/spec.md` via a change delta
- Focused persona/skill contract tests and validation evidence

No runtime, dependency, API, or consumer-application changes are expected.
