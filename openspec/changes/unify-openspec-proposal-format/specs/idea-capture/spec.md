# Delta for idea-capture

## MODIFIED Requirements

### Requirement: Proposal Structure

Every `proposal.md` MUST use the core structure returned by the selected
OpenSpec schema's `openspec instructions proposal` command and append the
mandatory Software Fabric extension sections. The extension MUST include scope,
non-goals, concise product scenarios, binary acceptance criteria, UX
applicability, Build/Buy/Vibe guidance, and applicable legal/IP notes. New
proposals MUST declare their new and modified capabilities using the CLI core
format rather than duplicate legacy capability headings.

#### Scenario: Proposal passes structure validation

- GIVEN a proposal follows the selected schema core and all applicable Software
  Fabric extensions
- WHEN the structure validator runs
- THEN the proposal is marked valid
- AND every declared capability maps to exactly one delta spec path

#### Scenario: Proposal fails structure validation

- GIVEN a proposal is missing a required schema core section or Software Fabric
  extension
- WHEN the CI structure validator runs
- THEN the proposal is marked invalid and handoff remains blocked
- AND the failure identifies each missing or conflicting section

## ADDED Requirements

### Requirement: Proposal format precedence

Proposal generation MUST treat the selected OpenSpec CLI instruction output as
the source for schema-specific core headings and MUST treat repository guidance
only as the Software Fabric extension and policy layer.

#### Scenario: New proposal follows selected schema

- GIVEN an initialized project with a selected OpenSpec schema
- WHEN the Product Owner requests proposal instructions
- THEN it creates the core proposal sections from the returned template and
  instruction
- AND appends the required repository extension sections
- AND does not substitute a stale repository copy of the package template

#### Scenario: Conflicting rules cannot be reconciled

- GIVEN repository guidance requires a heading or behavior that directly
  contradicts the selected schema
- WHEN proposal generation evaluates the conflict
- THEN it stops before creating or updating the proposal
- AND reports the conflicting sources and the decision required to proceed

### Requirement: Proposal capability traceability

Every capability declared by a proposal MUST identify an exact new or existing
capability path and MUST correspond to exactly one delta spec in the change.

#### Scenario: Declared capability has a matching delta

- GIVEN a proposal declares `idea-capture` as a modified capability
- WHEN proposal planning is validated
- THEN `specs/idea-capture/spec.md` exists in the change
- AND the delta represents the declared requirement changes

#### Scenario: Capability mapping is missing

- GIVEN a proposal declares a capability with no corresponding delta spec
- WHEN proposal planning is validated
- THEN validation fails and identifies the missing capability path
- AND implementation readiness remains blocked

#### Scenario: Delta has no proposal capability

- GIVEN a change contains a delta spec whose capability is absent from the
  proposal
- WHEN proposal planning is validated
- THEN validation fails and identifies the undeclared delta
- AND the proposal or delta must be reconciled before handoff

### Requirement: Bounded legacy proposal compatibility

Validation MUST temporarily accept the legacy `Intent` and `Affected Domains`
headings for active proposals only when equivalent layered content is present;
newly generated proposals MUST use the selected schema headings.

#### Scenario: Active legacy proposal remains readable

- GIVEN an active proposal uses `Intent` instead of `Why` or `Affected Domains`
  instead of `Capabilities`
- WHEN compatibility validation runs
- THEN the compatible heading is recognized
- AND all mandatory Software Fabric extension requirements are still enforced

#### Scenario: New proposal does not emit legacy headings

- GIVEN the Product Owner generates a new proposal with the layered contract
- WHEN proposal capture completes
- THEN the CLI schema headings are used
- AND legacy headings are not emitted as primary proposal structure
