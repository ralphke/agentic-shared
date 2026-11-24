# Proposal

## Why

The canonical OpenSpec specifications and active delta changes are not currently
safe to treat as a single source of truth. One active change fails validation,
several completed changes contain deltas that can no longer archive, and the
persona and lifecycle specifications leave ownership and handoff boundaries
ambiguous.

## Scope

- Reconcile every critical finding from the repository-wide OpenSpec audit.
- Restore dropped scenarios in invalid `MODIFIED` requirements.
- Re-evaluate each dropped scenario for current relevance before restoring,
  revising, or intentionally removing it; a removal requires a reason and
  migration statement.
- Resolve stale `ADDED` requirements that already exist in canonical specs.
- Complete the Product Owner and UX Designer persona contracts.
- Clarify Product Owner proposal ownership and Systems Architect design
  ownership while preserving legitimate collaboration and defining a
  common-ground resolution path for disputed or overlapping responsibilities.
- Align canonical planning, UX applicability, quality-gate, sync, and archive
  requirements with the repository's mandatory workflow instructions.
- Normalize source-spec layout and delta-spec headings without changing unrelated
  product behavior.
- Permit a narrowly scoped HIGH/CRITICAL security override only for the
  devcontainer image validation lane, represented as an explicit warning with a
  mandatory remediation follow-up; do not permit that override to bypass any
  application, merge, release, deployment, or archive gate.
- Preserve and integrate the existing uncommitted edits in canonical specs.

## Out of Scope

- Implementing product or application features.
- Changing the stage order beyond what the accepted Software Fabric process
  already defines.
- Replacing OpenSpec with another planning system.
- Claiming completion of external tests, security review, legal approval, code
  review, CI, coverage, or operational gates.
- Archiving or deleting active changes as part of this proposal.

## UX Applicability

```json
{
  "required": false,
  "reason": "This change only reconciles specification structure, persona ownership, and lifecycle handoff policy; it does not alter a visual interface or user-facing interaction."
}
```

## What Changes

- Repair `migrate-prompts-to-openspec-skills` so its two `MODIFIED` requirements
  preserve every current scenario.
- Reconcile `add-ux-designer-persona`, `conditional-ux-stage-and-validation`, and
  `strengthen-ux-designer-brief-workflow` with requirements already present in
  the canonical personas spec.
- Expand the Product Owner and UX Designer persona requirements to include
  responsibilities, inputs, outputs, triggers, handoff entry criteria, blockers,
  and agent-file references.
- Make the Product Owner own raw-idea capture and proposal acceptance while the
  Systems Architect owns delta specs, design, and ordered tasks, and require
  collaborating roles to resolve justified overlaps without asserting exclusive
  ownership over a shared activity.
- Align `sdlc-process` quality gates and archive requirements with mandatory
  planning acceptance, task completion, scenario tests, sync verification,
  security, coverage, review, legal, CI, and applicable operations evidence.
- Add the required proposal UX applicability declaration to `idea-capture`.
- Remove duplicate Purpose sections from canonical specs and normalize active
  delta headers that do not use `# Delta for <domain>`.
- Remove strict-validation warnings from overlong requirements and persona
  requirements missing `MUST` or `SHALL` language while preserving intent.
- Define a devcontainer-only security exception that records each affected
  finding, evidence and justification, approving security reviewer, remediation
  owner, expiry or renewal point, and mandatory follow-up issue or task.

## Scenarios

### Canonical specs pass strict validation

- GIVEN all canonical and active OpenSpec artifacts are present
- WHEN `openspec validate --all --strict --json` runs
- THEN every artifact is valid with no errors or warnings

### Responsibilities and handoffs are unambiguous

- GIVEN a stage persona receives accepted work
- WHEN another role reads the persona and lifecycle contracts
- THEN the current owner, required inputs, expected outputs, completion evidence,
  next owner, and blocking conditions are explicit and non-contradictory

### Completed active deltas are reconcilable

- GIVEN an active change whose task list is complete
- WHEN its deltas are compared with canonical specs
- THEN every retained requirement is represented as `ADDED` or `MODIFIED`
  without attempting to add an existing requirement

### Mandatory gates cannot be bypassed

- GIVEN a change reaches archive review
- WHEN required acceptance, tests, security, coverage, review, CI, legal, sync,
  or operational evidence is missing
- THEN the specifications require the workflow to remain blocked
- AND missing evidence is not converted into approval or non-applicability

## Acceptance Criteria

- [ ] `openspec validate --all --strict --json` reports zero failed items and
  zero warning findings.
- [ ] The five critical findings from the audit are resolved with concrete
  evidence in the delta specs and source specs.
- [ ] Product Owner, UX Designer, and Systems Architect artifact ownership is
  unambiguous, while justified overlap is governed by explicit collaboration,
  escalation, and common-ground resolution; each handoff names inputs, outputs,
  next stage, evidence, and blockers.
- [ ] Every scenario omitted by a stale or invalid delta is individually
  reviewed and either retained, updated with an applicability reason, or
  intentionally removed with migration guidance.
- [ ] Every canonical persona requirement uses explicit normative language and
  the persona contract fields required by the common layout.
- [ ] Every completed active delta is either archive-safe or explicitly
  reconciled without destructive deletion of valid requirements.
- [ ] Canonical planning and archive gates match
  `.github/instructions/openspec-workflow.instructions.md`.
- [ ] A devcontainer HIGH/CRITICAL finding can be downgraded only to an explicit
  `security:devcontainer-warning` outcome with mandatory follow-up; it cannot
  be represented as passed security evidence for merge, release, deployment,
  or archive.
- [ ] Existing uncommitted spec improvements are preserved or intentionally
  superseded with equivalent content.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `personas`: Complete persona responsibilities and accountable, collaboration
  aware handoff contracts; make normative language explicit.
- `sdlc-process`: Align ordered handoffs, planning acceptance, quality gates,
  delta synchronization, and archive blocking with mandatory policy.
- `idea-capture`: Require scope-backed UX applicability and make proposal
  ownership and acceptance unambiguous.
- `security-standards`: Define a narrow, auditable, temporary devcontainer
  validation exception without weakening production or archive security gates.

## Affected Domains

- `personas`
- `sdlc-process`
- `idea-capture`
- `security-standards`

## Impact

- Changes planning contracts under `openspec/specs/` and active changes under
  `openspec/changes/`.
- May update persona definitions and workflow instructions if implementation
  exposes contradictions, but no runtime application API is affected.
- No dependency, deployment, data, or visual-interface changes are required.
