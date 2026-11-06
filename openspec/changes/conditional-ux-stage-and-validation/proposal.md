# Proposal

## Why

UX responsibilities exist in personas and active deltas, but canonical specs,
architecture and QA skills, and automated test gates are not fully aligned.
Requiring a UX brief for every change also imposes unnecessary work on CLI-only,
API-only, framework, and other changes without an affected visual interface.

## UX Applicability

```json
{
  "required": false,
  "reason": "Shared SDLC governance change; no application visual surface is affected."
}
```

## What Changes

- Make UX applicability an explicit, scope-backed decision in the accepted
  proposal, assessed per change rather than inferred from the repository type.
- Route changes affecting a visual user interface through Product Owner,
  UX Designer, and Architect. Route changes without an affected visual
  interface directly from Product Owner to Architect.
- Require no UX design stage, `ux-brief.md`, UX-specific delta requirements,
  or UX tests for CLI-only, API-only, framework, and other nonvisual changes.
  Record the applicability decision in existing planning artifacts, not in a
  new UX exemption document. Normal functional specs and tests remain required.
- Treat unknown or conflicting applicability as a planning blocker, not as
  permission to skip UX. In mixed changes, apply UX only to affected visual
  surfaces and retain ordinary tests for CLI, API, and framework behavior.
- Align relevant personas, skills, shared instructions, planning entry points,
  and orchestrator guidance with the conditional handoffs. Remove the current
  requirement to create nonvisual UX briefs merely to mark checks inapplicable.
- Align the canonical `personas`, `sdlc-process`, and `testing-standards`
  specs, including relevant lifecycle diagrams and handoff contracts. Reconcile
  overlapping active UX deltas so a later sync cannot restore unconditional UX.
  Use the approved spec-sync workflow; do not archive existing changes or sync
  unrelated requirements as part of this work.
- For applicable visual changes, map each UX criterion to a test or documented
  validation check. Include applicable interaction states, accessibility,
  responsive form factors, keyboard, and touch behavior, with explicit reasons
  for dimensions that do not apply.
- Require actual UX validation evidence before applicable test-stage completion.
  Unperformed or unavailable required checks remain unresolved, not passed.
  Code coverage alone does not demonstrate UX correctness.
- Update test-stage automation to validate applicability and evidence, and run
  the consumer's configured UX checks where applicable. Do not prescribe a
  universal browser framework or add frontend tooling to nonvisual consumers.
- Add focused regression tests for visual, CLI-only, API-only, mixed, and
  missing or conflicting applicability paths.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `personas`: Conditional UX ownership, Product Owner routing, Architect and
  Developer inputs, and QA's applicable UX validation and evidence contract.
- `sdlc-process`: Conditional proposal-to-design routing, applicability-aware
  artifact gates, and reconciliation of the lifecycle documentation.
- `testing-standards`: UX criterion traceability and applicable validation
  evidence, with explicit nonvisual exemptions from UX-only obligations.

## Non-Goals

- Exempting nonvisual changes from normal planning, functional scenarios,
  automated tests, coverage where applicable, security, or conditional legal
  review.
- Adding application UI, browser-test infrastructure, or a new product runtime.
- Mandating UX work for CLI usability, API ergonomics, or framework contracts.
  Their accepted functional requirements remain with architecture and QA.
- Claiming accessibility compliance, real-device coverage, or successful
  consumer UX execution without evidence.
- Archiving changes or bypassing existing approval and release gates.

## Acceptance Criteria

1. A CLI-only or API-only proposal can reach architecture and testing without
   a UX stage, UX brief, UX-specific specs, or UX tests.
2. A change affecting a visual UI requires a completed UX brief before
   architecture and traceable UX validation evidence before test completion.
3. Missing or contradictory applicability cannot silently select the
   nonvisual route; a PR containing several changes is checked per change.
4. Mixed changes require UX work only for their affected visual surfaces.
5. Canonical specs, overlapping UX deltas, personas, skills, and workflow
   guidance agree on both routes without requiring an exemption-only UX file.
6. Focused tests verify both permitted nonvisual routes and blocked visual
   routes, including missing briefs, missing evidence, and ambiguous scope.
7. Normal functional tests and existing mandatory quality gates remain intact.

## Scenarios

- GIVEN a CLI-only or API-only change with accepted nonvisual applicability,
  WHEN proposal, design, and test gates run,
  THEN no UX artifact or UX test is required and functional gates still run.
- GIVEN an accepted change affecting a visual interface,
  WHEN architecture begins,
  THEN a completed UX brief is required and its criteria feed design and QA.
- GIVEN a visual change with passing code-coverage checks but missing required
  UX validation evidence,
  WHEN test completion is evaluated,
  THEN the change cannot claim the UX validation gate passed.
- GIVEN missing or conflicting applicability evidence,
  WHEN a handoff is requested,
  THEN clarification is required rather than silently bypassing UX.
- GIVEN a change containing both visual and nonvisual work,
  WHEN QA plans validation,
  THEN UX criteria cover affected visual surfaces and functional tests cover
  the remaining behavior without inventing nonvisual UX obligations.

## Impact

Changes affect shared persona and skill guidance, relevant Software Fabric
instructions, the SDLC orchestrator, focused contract and gate tests, and
OpenSpec requirements. Existing consumers with mandatory nonvisual briefs gain
a direct architecture route; visual consumers retain UX obligations.

The two active UX changes currently assume an unconditional UX handoff or a
nonvisual brief. Their overlapping requirements need explicit reconciliation,
not blind sequential synchronization. The proposal was accepted in conversation;
implementation still requires accepted specs, design, and tasks.

This is shared governance work with no new regulated-data handling,
third-party components, or content sources identified. Existing legal-risk
assessment and escalation rules remain unchanged.
