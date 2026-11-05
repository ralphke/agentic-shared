# Design

## Context

The shared assets define personas in `.github/agents/`, stage routing in
`.github/workflows/sdlc-orchestrator.yml`, and the persona roster in
`.github/instructions/sdlc-fabric.instructions.md` and `openspec/config.yaml`.
See `proposal.md` for motivation and the delta specs for required behavior.

## Goals / Non-Goals

**Goals:**

- Make UX a first-class, gated stage that produces a stable input for
  architecture and QA.
- Keep consumer implementation choices and existing security/legal gates with
  their current owners.

**Non-Goals:**

- Build application UI, widgets, prototypes, or device-specific implementations
  in this shared-assets repository.
- Add a framework, runtime dependency, or technology-specific design tool.

## Decisions

1. **Add conditional `stage:ux` before `stage:design` for visual changes.** A distinct
   label makes ownership and handoff observable. An optional Architect
   consultation was considered, but it would not ensure UX requirements are
   produced before implementation planning.
2. **Use `ux-brief.md` as the handoff contract.** The UX stage validates that a
   proposal exists and directs the UX Designer to create the brief; the
   design gate requires a UX brief only for affected visual interfaces.
   Nonvisual CLI/API/framework changes go directly to architecture without UX
   artifacts or UX tests. Embedding the
   brief in `design.md` was considered, but a separate artifact keeps UX
   acceptance criteria independently reviewable and available to QA.
3. **Keep the brief technology-neutral.** The Architect owns and justifies stack
   selection and provides enough implementation, dependency, and build/test
   detail for the Developer. The UX Designer may flag apparently obsolete or
   infeasible proposal choices with evidence, but does not recommend a
   replacement.
4. **Preserve downstream ownership and gates.** The Architect consumes the
   brief, the Developer implements approved tasks, and QA validates the UX
   criteria. Security remains after QA and before review; conditional legal
   review remains between security and code review.
5. **Express device validation as consumer QA evidence.** The shared assets
   define expected coverage across desktop, tablet, and mobile, plus keyboard
   and touch interactions. This repository has no running UI, so it cannot
   claim rendered-widget test results.

## Risks / Trade-offs

- **New required stage adds planning time** → Keep the UX brief proportionate
  to the proposal and focused on affected user journeys.
- **Existing proposals may lack applicability** → Record the accepted decision
  before the next handoff; require briefs only for visual changes.
- **Consumer device coverage may vary** → Require QA to document which form
  factors and interaction modes were checked and record any unavailable
  environment as a blocker rather than claiming coverage.

## Migration Plan

1. Add the UX persona, roster references, and `stage:ux` orchestrator gate.
2. Update the design gate to require `ux-brief.md` only for visual changes.
3. For in-flight work, record applicability and create a brief only if required.
   The accepted conditional-UX change governs the current routing contract.
4. Roll back by reverting the persona, roster, workflow, and spec changes
   together; no consumer application data or runtime migration is required.
