# UX Designer Guidance Quality Assessment

## Method

This is a lightweight document review, not user research or a usability study.
The baseline is repository revision `08748a2`, before the UX skill and persona
updates. Each dimension uses the same scale:

- **0** — absent
- **1** — mentioned, but not consistently actionable or verifiable
- **2** — explicit, repeatable, and suitable for downstream handoff

## Baseline and Updated Guidance

### Clarity — 1 to 2

- **Baseline:** The persona asked the agent to identify user goals and journeys
  from the accepted proposal and to ask the Product Owner when requirements
  were unclear (`.github/agents/ux-designer.agent.md`, `Core Responsibilities`
  and `Behaviour Rules`, revision `08748a2`).
- **Updated:** The persona and
  [UX design skill](../.github/skills/ux-design/SKILL.md) distinguish source-
  backed facts, assumptions, and unknowns, and define when clarification blocks
  handoff.

### Structure — 1 to 2

- **Baseline:** The persona had a useful checklist, but no standard structure
  for the delivered `ux-brief.md` (`UX Brief Checklist`, revision `08748a2`).
- **Updated:** The skill provides a brief structure for scope, user evidence,
  assumptions, journeys and states, content, accessibility, acceptance
  criteria, risks, and QA handoff.

### Execution Guidance — 1 to 2

- **Baseline:** The persona named important UX concerns, including WCAG 2.2 AA
  and responsive form factors, but did not define an ordered method for
  translating them into specific criteria (revision `08748a2`).
- **Updated:** The skill provides ordered steps for scope and evidence,
  journeys and states, content, accessibility and form factors, verifiable
  criteria, and risks. Checks are conditional on the actual experience.

### Handoff Quality — 1 to 2

- **Baseline:** The persona required QA validation criteria and an Architect
  handoff, but did not require each criterion to identify its source need or
  have a stable ID (revision `08748a2`).
- **Updated:** The skill requires observable Given/When/Then criteria with a
  source need and stable ID, leaves test selection and evidence to QA, and
  keeps blocking questions from being presented as ready work.

## Evidence and Limitations

The after-state is represented by
[ux-designer.agent.md](../.github/agents/ux-designer.agent.md),
[ux-design/SKILL.md](../.github/skills/ux-design/SKILL.md), and focused
contract tests in `tests/test_ux_designer_stage.py`. These checks validate
instruction structure and critical constraints; they do not prove that a
future brief is correct for a specific user or that an implementation conforms
to WCAG. Those require the relevant product evidence and QA validation.
