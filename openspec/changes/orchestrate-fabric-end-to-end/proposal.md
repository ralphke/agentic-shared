# Proposal: End-to-End Software Fabric Orchestration

## Why

The SDLC Orchestrator currently posts handoff comments and runs selected
label-driven checks, but does not execute the stage agents or advance their
work. Maintainers cannot reliably distinguish completed work from skipped
jobs, and must manually connect most stages.

The observed workflow history contained 13 runs: eight skipped, four failed,
and one successful run that performed only structural checks. Improvement
report #2 also recorded zero stage-label coverage. These are point-in-time
observations from 2026-11-09, not proof of successful lifecycle execution.

## Intent

Make the shared Software Fabric orchestrator coordinate actual agent execution
from authorized idea intake through planning, implementation, testing, security,
conditional legal review, code review, configured deployment, operations, and
verified archive. Reuse existing persona definitions, Fabric skills, OpenSpec
mechanics, and trusted evidence controls rather than inventing a parallel SDLC.

End-to-end means a resumable workflow with explicit human approval boundaries,
not unattended authority to merge, deploy, or waive gates. Every stage must
expose its owner, execution reference, evaluated revision, result, and next
action, including when execution is unavailable or blocked.

## What Changes

- Replace comment-only handoffs with supported, observable agent dispatch and
  completion handling. Compare execution options before selecting the runtime.
- Default eligible unlabeled Fabric work to proposal, detect conflicting stage
  labels, and reconcile the existing Copilot Task Router so intake cannot
  directly authorize implementation.
- Preserve explicit Proceed before capture, proposal acceptance before design,
  and current proposal/spec acceptance plus implementation authorization before
  code. Bind approvals to their actual content and invalidate stale evidence.
- Advance stages only after independently verified outputs and applicable
  gates, including conditional UX and legal routing and bounded rework.
- Retain durable change/run identity, sticky mode/store context, revision
  binding, duplicate-event protection, concurrency control, cancellation,
  bounded retries, and recovery after workflow or agent interruption.
- Coordinate post-merge deployment and operations through configured consumer
  adapters with outcome evidence. Missing adapters block applicable work.
- Route merge/release/archive through existing trusted controls. The disabled
  protected-operations opt-in must never become approval or successful delivery.
- Publish current status and reasons on the linked issue/PR and Actions summary;
  comments and labels describe progress but do not prove execution or approval.
- Preserve consumer-local specifications, local extensions, and unchanged
  upstream OpenSpec skill ownership during shared synchronization.

## Scope

Shared orchestrator and task-router workflows, bounded execution integration,
existing agent/skill handoff contracts, configuration and administrator guidance,
scenario tests, and an isolated end-to-end execution demonstration.
The demonstration must distinguish fixture/dry-run validation from actual
authorized agent execution; neither implies production clearance.

## Out of Scope

- Changing or forking the upstream OpenSpec CLI or generated skills.
- Removing human acceptance, security, legal, review, operational, or archive
  requirements; treating generated text or task completion as trusted approval.
- Automatically enabling protected operations, configuring live credentials or
  branch protection, or merging/deploying from this planning request.
- Building a general-purpose agent platform, application, or hosted UI.
- Inventing consumer infrastructure, deployment targets, SLOs, or exemptions.
- Implementing every candidate agent runtime; select one supported baseline.

## Approach

Use OpenSpec to resolve planning artifacts and task readiness, Fabric skills
to define the applicable stage procedure, and existing personas to execute
bounded stage work. A deterministic coordinator validates transitions and
evidence outside the agent's own claims. Planning state and execution state
are related but distinct; OpenSpec CLI readiness does not establish approval.

Select a supported execution mechanism after reviewing cloud-agent APIs,
programmatic Copilot CLI, Copilot SDK, and GitHub Agentic Workflows. Verify
authentication, repository/plan availability, persona/tool compatibility,
completion signals, cost bounds, and resume behavior before committing to one.
Use least privilege and isolate untrusted content/code from privileged control
and deployment credentials. Keep execution credentials distinct from gate-App
credentials and independently authorized dispositions.

## UX Applicability

```json
{
  "required": false,
  "reason": "The change coordinates existing repository agents and workflows and reports through standard issue comments and Actions summaries; it introduces no custom visual interface."
}
```

## Scenarios

### Accepted work executes the existing stage personas

- GIVEN authorized intake and a configured execution mechanism
- WHEN the coordinator starts a Fabric change
- THEN the Product Owner executes the existing proposal procedure
- AND subsequent applicable personas execute only after their prerequisites
  and explicit approval boundaries pass
- AND every execution and handoff has a verifiable reference.

### Missing acceptance or changed planning blocks implementation

- GIVEN artifacts are ready but current proposal/spec acceptance or explicit
  implementation authorization is missing or stale
- WHEN an event requests implementation
- THEN no implementation agent is dispatched
- AND the coordinator names the required approval and affected content.

### Duplicate or delayed events do not repeat stage work

- GIVEN a stage is running or has completed for a specific change revision
- WHEN duplicate, concurrent, or out-of-order events arrive
- THEN the coordinator reconciles existing state without duplicate dispatch
- AND stale results cannot advance the current revision.

### Failed or unavailable execution remains visible

- GIVEN an agent fails, times out, requests clarification, or lacks credentials
- WHEN its stage result is processed
- THEN the change reports failed or blocked with a concrete next action
- AND it does not advance through a success-shaped fallback
- AND authorized recovery respects bounded retries and prior work.

### Disabled protected operations cannot complete delivery

- GIVEN merge/release controls are disabled or required evidence is absent
- WHEN pre-delivery work finishes
- THEN the coordinator reports the blocked boundary
- AND does not merge, publish, deploy, or archive through another route.

### Configured deployment and operations finish the lifecycle

- GIVEN required reviews and protected merge/release conditions pass
- WHEN authorized consumer adapters complete deployment and operations
- THEN their evidence binds the deployed revision and applicable stability gates
- AND complete delta verification and fresh archive evidence precede sync/move
- AND absent adapters or operational evidence block applicable completion.

## Acceptance Criteria

- [ ] One execution mechanism is selected through a documented, source-backed
      comparison and verified against the target repository prerequisites.
- [ ] Existing stage personas and Fabric/OpenSpec procedures actually execute
      through the selected mechanism; comments alone cannot satisfy a stage.
- [ ] Every eligible event reports its route, current stage, status, execution
      reference when dispatched, and blocker/next action rather than silent skips.
- [ ] Intake, planning acceptance, implementation authorization, conditional
      UX/legal routing, and revision invalidation have passing scenario tests.
- [ ] Duplicate/concurrent/stale events, interruption, cancellation, bounded
      retries, and rework do not duplicate work or bypass approval boundaries.
- [ ] Agent self-reports, labels, or generic check names cannot replace trusted
      gate evidence; disabled controls and missing adapters block delivery.
- [ ] An authorized isolated demonstration records actual stage executions and
      a negative path; production actions require separate authorization.
- [ ] Consumer ownership, local stores, upstream skills, permissions, credential
      separation, installation prerequisites, and rollback are documented/tested.

## Capabilities

### New Capabilities

None; extend the existing lifecycle and persona contracts.

### Modified Capabilities

- `sdlc-process`: executable, resumable, approval-gated stage coordination.
- `personas`: bounded invocation, outputs, and verifiable completion contracts.
- `testing-standards`: transition, recovery, and end-to-end orchestration tests.
- `operations`: configured deployment/operations handoffs and execution visibility.

## Affected Domains

`sdlc-process`, `personas`, `testing-standards`, `operations`.

## Build/Buy/Vibe Flag

**Adopt** a supported existing agent execution service/runtime. **Build** only
the bounded Fabric coordinator and adapters needed to connect existing assets.
Do not build another general-purpose agent execution platform.

## Legal/IP Notes

Agent execution can transmit repository content to a selected AI service and
incur usage charges. Verify service authorization, repository access, applicable
terms, content rights, retention, and permitted data handling before execution.
Do not introduce a new provider or send sensitive content under this proposal.
Escalate actual regulated-data, unclear rights, or policy-gap triggers to the
Legal & Compliance stage; proposal acceptance is not external-service consent.

## Impact

Affects shared Actions orchestration, consumer configuration, persona/skill
handoffs, evidence integration, and tests. Runtime dependencies, authentication
and billing requirements remain subject to the execution-mechanism decision.
Related backlog: #21 (security workflow coverage) and #22 (protected operations
setup). Neither is silently treated as completed or waived by this change.
