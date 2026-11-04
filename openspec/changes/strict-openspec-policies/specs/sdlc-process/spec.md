# Delta for sdlc-process

## ADDED Requirements

### Requirement: Pre-Capture Intake Decision

Before any repository capture write, the workflow MUST allow explicit Proceed,
Defer, or Do not pursue. Ideas and draft proposals MUST remain in conversation
or session storage until Proceed. An explicit request to create named repository
artifacts MAY supply Proceed without a duplicate prompt. Defer or rejection
MUST stop intake without repository writes or successful archive claims.

#### Scenario: Reject or defer before capture

- GIVEN an idea or draft proposal has not been captured in repository files
- WHEN the requester chooses Defer or Do not pursue
- THEN no change folder, metadata, planning artifacts, or implementation is written
- AND no delivery gates are required just to end intake
- AND no successful archive, task completion, or main-spec synchronization is claimed

#### Scenario: Missing capture decision does not write

- GIVEN a raw idea, an idea issue, P0 priority, or a kickoff request
- WHEN no explicit Proceed or request for named repository artifacts is present
- THEN the workflow assesses and presents the intake choices without repository writes
- AND missing input keeps capture paused rather than assuming consent

#### Scenario: Proceed authorizes capture only

- GIVEN a completed intake assessment
- WHEN the requester explicitly chooses Proceed or requests named repository artifacts
- THEN capture may begin without asking the same intake question again
- AND current proposal/spec acceptance and implementation/archive gates still apply

#### Scenario: Rejection preserves existing work

- GIVEN a proposal or change already has repository files
- WHEN the requester rejects or defers it
- THEN the workflow stops without deleting or reverting those files
- AND it does not mark the change successfully archived
- AND any cleanup needs separate explicit authorization

## MODIFIED Requirements

### Requirement: Spec Before Code

A complete OpenSPEC spec with scenarios MUST exist and be accepted before any
implementation task is assigned. Required proposal, specs, design, and tasks
MUST be substantively complete before implementation. Explicit acceptance of the
current proposal/spec MUST be verifiable; CLI readiness, schema omissions, and
skipped statuses MUST NOT waive these prerequisites.

#### Scenario: Implementation blocked without spec

- GIVEN a developer attempts to open a PR referencing a change
- WHEN the CI orchestrator checks for `openspec/changes/<change>/tasks.md`
- THEN the PR is blocked if tasks.md is missing or has no checked-off items
- AND the PR receives a `spec-required` label

#### Scenario: Accepted proposal produces spec, design, and tasks

- GIVEN an accepted `proposal.md` with >=3 scenarios
- WHEN the Architect Agent reviews it
- THEN a `specs/<domain>/spec.md` delta is produced for each affected domain
- AND `design.md` is produced with ADRs and a component diagram
- AND `tasks.md` is produced with numbered, atomic, ordered tasks
- AND implementation cannot begin until all three artifact types exist

#### Scenario: Apply rejects incomplete or unaccepted planning

- GIVEN tasks exist but required planning is missing, incomplete, or skipped
- OR acceptance evidence for the current proposal/spec is absent or stale
- WHEN an apply instruction, persona, or onboarding flow attempts implementation
- THEN implementation stops and names the missing prerequisite
- AND a ready CLI state or user confirmation cannot override it
- AND task checkboxes are not pre-completed to satisfy a PR-progress check

### Requirement: Automated Quality Gates

Every change MUST pass all quality gates before `/opsx:archive` is invoked.
Unmet or unverifiable mandatory gates MUST block single and bulk archive before
sync writes or moves. User confirmation MUST NOT waive these gates.

**Gate checklist:**

- [ ] All CI checks green (build, lint, unit tests)
- [ ] No HIGH or CRITICAL vulnerabilities in security scan
- [ ] Code coverage >= 80% on new code
- [ ] At least one review approval (human or AI code-reviewer)
- [ ] All acceptance criteria in spec checked off

#### Scenario: Security gate blocks merge

- GIVEN a PR with a HIGH severity vulnerability detected by the Security Agent
- WHEN the security gate runs in CI
- THEN the PR merge is blocked
- AND a linked issue is automatically opened with remediation steps
- AND the Security Engineer Agent is assigned

#### Scenario: Coverage gate blocks merge

- GIVEN a PR where new code coverage is 65% (below 80% floor)
- WHEN the CI coverage check runs
- THEN the PR is labelled `coverage-insufficient`
- AND the QA Engineer Agent is notified to add tests

#### Scenario: Missing evidence cannot be confirmed away

- GIVEN a required gate is unmet or lacks usable evidence
- WHEN the user confirms an archive request
- THEN the affected change remains active without sync writes or moves
- AND the missing evidence is reported separately from genuinely optional warnings
- AND local artifact validation is not treated as proof of external quality gates

### Requirement: Spec Archive on Completion

When all gates pass and required artifacts and tasks are complete, every change
delta MUST be merged into the main `specs/` source of truth and verified before
the change folder is archived. Single and bulk archive MUST NOT exclude deltas,
skip sync verification, or accept confirmation as an override.

#### Scenario: Successful archive

- GIVEN all tasks in `tasks.md` are checked off
- AND all quality gates have passed
- WHEN `/opsx:archive` is invoked
- THEN delta specs from `changes/<slug>/specs/` merge into `openspec/specs/`
- AND the change folder moves to `openspec/changes/archive/`
- AND the merged spec reflects the ADDED/MODIFIED/REMOVED sections

#### Scenario: Archive blocked by incomplete gates

- GIVEN a change where CI is still failing
- WHEN `/opsx:archive` is invoked
- THEN the archive is rejected with a list of failing gates
- AND no files are moved or modified

#### Scenario: Incomplete required artifacts or tasks block archive

- GIVEN a required artifact is missing, incomplete, or skipped, or tasks remain
  incomplete or cannot be verified
- WHEN single or bulk archive checks readiness
- THEN the affected change is blocked before sync or move
- AND optional-artifact warnings alone do not block otherwise eligible changes

#### Scenario: Bulk archive cannot exclude an unsatisfied delta

- GIVEN one delta lacks implementation evidence or has an unresolved conflict
- WHEN bulk archive evaluates its parent change
- THEN the entire affected change is blocked rather than archived partially synced
- AND every delta of each eligible change is synced and verified before its move
- AND unresolved contradictions between accepted changes are reported, not silently
  overwritten by chronological ordering

#### Scenario: Sync failure keeps the change active

- GIVEN sync or comparison fails for any delta
- WHEN archive processes the change
- THEN the change folder remains active
- AND any main-spec writes already made are reported without claiming rollback
