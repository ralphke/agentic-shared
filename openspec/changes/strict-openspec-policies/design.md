# Design

## Context

See proposal.md for motivation and specs/sdlc-process/spec.md for behavior.
Generated command assets currently supply permissive paths even though the
source spec requires complete planning, mandatory gates, and merged deltas.
The user accepted the proposal in this conversation before this design.

## Goals / Non-Goals

**Goals:** Make every operational entry point agree on prerequisites; keep
existing root, schema-path, task-location, and semantic sync contracts intact.

**Non-Goals:** A new runtime enforcement engine, approval format, stage,
dependency, broad CI rewrite, or source-spec sync/archive during implementation.

## Decisions

### ADR: One pre-capture intake decision, not a delivery-gate waiver

Assess the idea or draft proposal in conversation or session storage before the
first repository write, CLI scaffold, or initialization. Offer Proceed, Defer,
and Do not pursue once. A direct request to create named repository artifacts
is explicit Proceed and is not asked again. Raw ideas, issue labels, P0 priority,
and kickoff do not supply that decision. Defer or rejection ends intake without
repository writes, deletion, or completion/archive claims.

Wire this boundary into central instructions, intake/kickoff/persona paths, and
proposal/fast-forward/onboarding capture entry points. Existing explore capture
confirmation remains valid. No new slash command, schema flag, state file,
rejected-change archive, or cleanup mechanism is introduced. Existing tracked
proposals are preserved if rejected; removing them requires separate explicit
authorization. A capture decision is not proposal acceptance or permission to
implement.

Alternative: using `skip_specs` or archive to discard rejected ideas would mix
intake abandonment with successful delivery and weaken the restored gates.

### ADR: Central mandatory contract with explicit operational checks

Define required artifact roles, current acceptance evidence, and archive gates
in the shared OpenSpec instructions. Skills/prompts explicitly perform these
checks rather than relying solely on config guidance or CLI existence status.
Resolve custom schema paths using status/context output; ambiguous or omitted
required roles block. Optional artifacts remain warnings. Existing approval
evidence is used rather than adding an approval file.

Alternative: changing CLI schemas or trusting `applyRequires` alone cannot
establish substantive completeness, acceptance, or external gate evidence.

### ADR: Archive eligibility is per whole change

Single archive offers sync/verification or cancellation, never unsynced archive.
Bulk preflight excludes blocked whole changes before conflict resolution.
All deltas of an eligible change are synced and verified; missing implementation
blocks its parent, and contradictions require resolution rather than last-write
wins. Direct user-requested partial sync remains supported but proves no archive
readiness. Preserve existing retirement and collision rules.

Alternative: per-delta exclusions can archive a change whose main spec never
reflects its accepted requirements.

### ADR: Bounded restoration plus committed-body regression contracts

Update the owned apply policy block in both script and committed skill.
Preserve restoration's narrow targets and fail-closed preflight; do not make a
generic generated-body rewriter. Add tests over operational bodies to detect
known bypasses and positive prerequisites after regeneration. README documents
manual reconciliation beyond restoration.

### ADR: Artifact validation is necessary, not sufficient

Reject empty required files, absent usable tasks, and unfinished task markers.
Use temporary fixtures for complete and incomplete cases. Preserve CLI-driven
schema paths in agent workflows; the existing conventional-path validator
retains its documented bounded role. Do not claim its success verifies CI,
review, security, acceptance, or SLOs.

## Component Diagram

```text
Accepted proposal/spec + complete design/tasks
                    |
    central OpenSpec/Fabric instructions
           /                     \
 apply + onboarding         archive + bulk archive
     |                       | gates before writes
 Developer handoff           v
                       sync every delta -> verify -> move
           \                     /
           policy/restoration/validator fixture tests
```

## Risks / Trade-offs

- Generated bodies may regress after CLI update -> committed contract tests
  and mandatory diff review, not restoration alone.
- External gates are unavailable locally -> report unverifiable blockers;
  no success-shaped fallback or archive claim.
- Shared-capability deltas may supersede each other -> explicit evidence-backed
  ordering; block unresolved conflicts instead of excluding deltas.
- A failed sync may have partial writes -> report them and keep the change active.
- Existing source PR-progress condition requires checked tasks -> preserve it;
  never pre-check tasks to satisfy implementation-entry requirements.

## Migration Plan

Publish shared assets through normal versioned consumer sync after review.
Keep this change active until mandatory review/CI/security gates pass.
Rollback is a normal reviewable revert of these bounded policy edits, never
an automatic weakening of required gates. No legal-risk trigger was identified:
this change introduces no data handling, dependency, service, or rights exposure.
