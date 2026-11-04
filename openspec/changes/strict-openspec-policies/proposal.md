# Proposal

## Why

Generated apply and archive instructions contradict the existing Software Fabric
gates by permitting premature implementation, confirmation overrides, and archive
without complete spec synchronization. Restore operational agreement with
`openspec/specs/sdlc-process/spec.md` rather than expanding the lifecycle.

## What Changes

- Add one pre-write intake decision: Proceed, Defer, or Do not pursue. Assess
  ideas and draft proposals in chat/session storage; only explicit Proceed
  authorizes repository capture. Early rejection needs no delivery gates and is
  not successful archive or permission to delete existing work.
- Require complete proposal, delta specs, design, and tasks, with explicit
  acceptance of the current proposal/spec before implementation.
- Block archive when required artifacts/tasks or mandatory quality gates are
  incomplete or unverifiable; confirmation and skipped statuses cannot waive them.
- Require sync and verification of every delta before single or bulk archive.
  Block the whole affected change when implementation or conflict resolution
  is missing instead of archiving it with excluded deltas.
- Align instructions, skills, prompts, onboarding, persona handoffs, config,
  bounded restoration contracts, validator fixtures, and directly related docs.
- Preserve optional-artifact warnings, selected-store paths, task source
  locations, collision handling, retirement rules, and advisory guidance.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `idea-capture`: Require explicit Proceed before repository capture through
  any intake channel; retain automatic drafting of complete ideas after Proceed.
- `sdlc-process`: Clarify existing Spec Before Code, Automated Quality Gates,
  and Spec Archive on Completion requirements with fail-closed scenarios and
  explicit non-overridable prerequisites; define the pre-capture intake exit.

## Scope and Non-goals

Only shared governance assets and their existing local validation are in scope.
Do not add stages, an approval-record format, a runtime gate service, deployment
features, or branch-protection changes. Do not create a PR or archive this change
on the strength of local checks alone.

## Scenarios

### Rejected or deferred intake leaves the worktree untouched

- GIVEN an idea or draft proposal is being assessed before repository capture
- WHEN the requester chooses Defer or Do not pursue
- THEN no change folder, metadata, proposal, spec, design, tasks, or code is written
- AND no successful archive, completed tasks, or delivery clearance is claimed
- AND any existing files are preserved

### Explicit proceed captures planning without accepting it

- GIVEN intake assessment is complete and no capture decision has been made
- WHEN the requester explicitly chooses Proceed
- THEN repository capture may start using the normal OpenSpec workflow
- AND proposal/spec acceptance and implementation/archive gates remain separate
- AND an explicit request to create named repository artifacts can count as Proceed,
  while a raw idea, issue label, priority, or kickoff alone cannot

### Required planning blocks implementation

- GIVEN a task file exists but a required artifact is missing or skipped, or
  acceptance of the current proposal/spec cannot be verified
- WHEN apply or onboarding attempts implementation
- THEN implementation stops and names the missing prerequisite
- AND CLI readiness or user urgency does not bypass the prerequisite

### Required completion blocks archive

- GIVEN required artifacts/tasks or a mandatory quality gate are incomplete or
  unverifiable
- WHEN single or bulk archive is requested
- THEN the affected change remains active without sync or move
- AND confirmation cannot override the blocker
- AND genuinely optional artifact warnings remain informative

### Every archived delta is synchronized

- GIVEN a change has multiple deltas and one is blocked, excluded, or unverified
- WHEN archive evaluates the change
- THEN the whole affected change remains active
- AND an eligible change is moved only after every delta has been synced and
  verified against the main specs

### Alternate paths obey the same gates

- GIVEN onboarding, a legacy prompt, persona, or regenerated command asset
- WHEN it directs implementation or archive
- THEN it preserves the same mandatory prerequisites
- AND focused regression checks reject known bypass wording

## Acceptance Criteria

- Raw ideas and draft proposals can be rejected or deferred before any repository
  write through a single explicit intake decision shared by entry points.
- Intake rejection/defer is not archive and never silently deletes existing work.
- Operational apply paths require substantive planning completeness and current
  explicit acceptance, not file existence or CLI-ready status alone.
- Archive paths distinguish required blockers from genuinely optional warnings;
  no confirmation override or archive-without-sync choice remains.
- Bulk archive never moves a change with an excluded or unverified delta.
- Policy restoration remains bounded, idempotent, and coherent with committed
  blocks; tests detect permissive generated-body regressions.
- Artifact validation rejects empty required files, missing usable tasks, and
  incomplete/unknown task markers; its limits regarding external gates are clear.
- Existing relevant tests and OpenSpec validation pass; changed files and exact
  validation results are reported, without claiming external gate clearance.

## Impact

Affects shared `.github` skills, prompts, instructions, personas, scripts and
their tests, the design-stage handoff, `openspec/config.yaml`, README guidance,
and this change's delta specs. No new dependencies are intended.

Legal-risk assessment: no sensitive data, new third-party components, external
services, or licensing/use-rights changes are introduced. No legal escalation
trigger is identified for this bounded policy alignment.
