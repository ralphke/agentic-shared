# Delta for sdlc-process

## ADDED Requirements

### Requirement: Explicit OpenSpec and Fabric Boundaries

Fabric-managed work MUST be distinguishable from explicitly selected
standalone OpenSpec work. Fabric guidance MUST identify its policies as
additional to OpenSpec behavior.

#### Scenario: Existing consumer uses Fabric

- GIVEN a consumer already uses the shared Fabric integration
- WHEN work is started without an explicit standalone selection
- THEN Fabric remains active and its applicable gates remain required

#### Scenario: Standalone OpenSpec is selected

- GIVEN a user explicitly selects standalone OpenSpec work
- WHEN the upstream workflow is invoked
- THEN Fabric-specific agent steps are not presented as OpenSpec requirements
- AND the selection does not bypass repository merge or release controls

#### Scenario: Invocation surfaces are distinguished

- GIVEN a user reads workflow guidance
- WHEN the guidance describes an OpenSpec action
- THEN it distinguishes terminal CLI operations from agent chat workflows
- AND identifies which additional behavior belongs to Fabric

### Requirement: Revision-Bound Fabric Gate Evidence

Fabric merge and release controls MUST evaluate trusted evidence for the
applicable gates at the relevant revision. Missing, stale, unverifiable, or
failed evidence MUST block the affected control.

#### Scenario: Required merge evidence is missing

- GIVEN a Fabric-managed pull request lacks a required gate result
- WHEN its merge control evaluates the current pull request head
- THEN the control fails and names the missing evidence
- AND no successful gate result is claimed

#### Scenario: Old evidence does not authorize a changed revision

- GIVEN required checks or approvals refer to an earlier revision
- WHEN the pull request head changes
- THEN those results do not authorize the new head
- AND current applicable evidence is required

#### Scenario: Applicable legal approval is absent

- GIVEN a change requires legal review
- WHEN the review or release control cannot verify its required disposition
- THEN the affected control remains blocked
- AND the missing disposition is reported

#### Scenario: Post-deployment evidence is evaluated at archive

- GIVEN an applicable operational gate can only be evaluated after deployment
- WHEN archive readiness is evaluated
- THEN the gate uses evidence for the deployed revision
- AND its absence cannot be treated as a successful archive gate

#### Scenario: Different evaluated and deployed revisions have trusted mapping

- GIVEN the evaluated change and deployed release use different revisions
- WHEN archive preflight verifies a fresh authorized mapping bound to the
  repository, change/store identity, both revisions, and externally verified
  PR, release/tag, and deployment/status references
- THEN applicable change gates use the evaluated revision
- AND operational gates use the mapped deployed revision
- AND the mapping does not waive any applicable gate

#### Scenario: Missing or mismatched revision mapping blocks archive

- GIVEN the evaluated and deployed revisions differ
- WHEN their mapping is missing, stale, duplicated, unauthorized, superseded,
  unavailable, or inconsistent with authenticated source records
- THEN archive-driven spec writes and moves are blocked
- AND ancestry, caller confirmation, or an author-supplied passing claim does
  not substitute for that mapping

### Requirement: Gate Enforcement Limits Are Visible

Fabric documentation MUST distinguish automated controls, required repository
configuration, and advisory agent guidance. It MUST NOT claim that direct
OpenSpec CLI operations enforce Fabric gates.

#### Scenario: Direct CLI archive is requested

- GIVEN a user can invoke the OpenSpec CLI directly
- WHEN the user reads Fabric archive guidance
- THEN the guidance explains that the CLI does not enforce Fabric preflight
- AND identifies the separately configured controls and their limitations

### Requirement: Consumer OpenSpec Store Ownership

Recommended consumer configuration MUST keep consumer product specifications
and changes local and use the shared store only when explicitly selected.

#### Scenario: Consumer creates a product change

- GIVEN the consumer follows the recommended synchronization configuration
- WHEN it creates a product change without selecting another store
- THEN its local OpenSpec root owns the change and product specifications
- AND synchronization preserves protected active changes

#### Scenario: Shared store is explicitly selected

- GIVEN a user selects the registered shared store
- WHEN the user performs store-aware OpenSpec operations
- THEN those operations target the selected shared store
- AND the selection is not inferred for consumer product work

## MODIFIED Requirements

### Requirement: Automated Quality Gates

Every Fabric-managed change MUST pass all applicable quality gates before
archive. Merge and release controls MUST enforce the gates applicable at their
respective lifecycle points using revision-bound evidence.

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
