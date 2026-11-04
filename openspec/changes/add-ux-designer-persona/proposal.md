# Proposal

## Why

The current Software Fabric has no explicit owner for UX, accessibility, or
responsive interaction requirements, so these concerns can be missed or left
implicit until implementation and testing. A UX Designer stage will make those
requirements a deliberate, reviewable input to architecture and QA.

## What Changes

- Add a UX Designer persona and a dedicated handoff between Product Owner and
  Systems Architect.
- Define a UX brief that captures user flows, readable and accessible
  interactions, responsive expectations across desktop, tablet, and mobile, and
  explicit visible controls and content.
- Require keyboard and touch interaction expectations and device/form-factor
  validation to be handed to QA; retain the existing security gate before
  review or deployment.
- Pass implementation constraints to the Architect: TypeScript is the default
  for consumer UI implementations; Rayfin is permitted only where the consumer
  architecture explicitly supports it. The shared persona assets do not
  implement widgets or select a consumer's stack.
- Update persona and SDLC specifications, the shared persona roster and
  instructions, and the orchestrator's stage handoff.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `personas`: Define the UX Designer's responsibilities, UX brief, quality
  checks, and handoff to the Systems Architect.
- `sdlc-process`: Add the UX stage between proposal and architecture and specify
  the downstream QA, security, and review gates.

## Impact

- Add `.github/agents/ux-designer.agent.md`.
- Update `.github/instructions/sdlc-fabric.instructions.md`,
  `.github/workflows/sdlc-orchestrator.yml`, `openspec/config.yaml`, and the
  personas and SDLC process specifications.
- No runtime application, UI widget, dependency, or API changes are in scope.
