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

## Conditional UX Follow-Up Assessment

This follow-up uses the same 0–2 rubric, comparing revision `1973062` with
the `conditional-ux-stage-and-validation` implementation. It evaluates
cross-stage guidance and enforcement, not the quality of a delivered product.
The earlier assessment above remains the historical persona/skill baseline.

### Conditional Routing Clarity — 1 to 2

- **Baseline:** UX concerns were detailed, but nonvisual products still needed
  a brief and explicit layout exclusions.
- **Updated:** The proposal records scope-backed applicability. Visual work
  receives UX design; CLI/API/framework-only work needs no UX design, briefs,
  UX-specific specs, reports, tests, or frontend tooling. Mixed changes limit
  UX duties to affected visual surfaces.

### Cross-Stage Structure — 1 to 2

- **Baseline:** The persona and skill described UX, but canonical persona,
  lifecycle, and testing specs did not consistently represent the role.
- **Updated:** The three canonical specs define conditional routing, stable
  criteria, QA evidence, and nonvisual exemptions. Older overlapping UX deltas
  are reconciled without erasing their historical task completion.

### Gate Execution Guidance — 1 to 2

- **Baseline:** QA guidance named UX checks without a shared completion gate.
- **Updated:** The shared helper checks applicability, criterion mappings,
  evidence, and configured current-head automation with bounded waiting.
  Nonvisual execution returns before reading UX files or contacting GitHub.
  Missing, failed, blocked, or stale required validation does not become a pass.

### Conditional Handoff Quality — 1 to 2

- **Baseline:** UX handoff was unconditional, and code coverage could pass
  without independently checked UX evidence.
- **Updated:** Architecture requires a brief only for visual scope; test
  completion and security entry require applicable UX evidence and successful
  consumer checks. Functional tests, coverage, security, and legal gates remain
  independently required.

### Verification Evidence and Boundaries

- The focused persona, helper, workflow, planning-skill, strict-policy,
  restoration, and consumer-sync suites pass: **68 tests and 423 subtests**.
- The helper's focused coverage run reports **96% combined line/branch
  coverage**, exceeding the 80% floor.
- Real CLI fixtures run CLI-only and API/framework-only declarations through
  every phase with only a proposal present. Visual workflow-command fixtures
  reject missing briefs and reports; mocked check-run fixtures reject missing,
  pending, stale, failed, skipped, cancelled, and ambiguous required checks.
- Windows fixture paths are resolved before direct parser tests so short-path
  aliases cannot turn intended parser assertions into unrelated path failures.
- Canonical specs pass ordinary validation. Strict mode retains **21 existing
  warnings**, compared with **24** at `1973062`, and introduces none.
- Markdown lint retains **157 pre-existing diagnostics in four files**,
  verified against `1973062`; changed content introduces no new diagnostics.
- These are contract and helper tests, not live browser, accessibility,
  usability, or real-device validation. Consumer check results are mocked;
  no production UX outcome or external CI/security/review gate is certified.
- The orchestrator is protected consumer infrastructure: adopt its workflow
  and helper together through a reviewed change, and configure the required
  check names for visual work.
