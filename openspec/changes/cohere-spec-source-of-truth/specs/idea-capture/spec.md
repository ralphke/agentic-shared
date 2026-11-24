# Delta for idea-capture

## MODIFIED Requirements

### Requirement: Proposal records UX applicability

Every proposal MUST contain exactly one `## UX Applicability` decision with a
boolean `required` value and a nonempty scope-backed reason. Missing, invalid,
duplicate, or contradictory applicability MUST block the proposal handoff.

#### Scenario: Visual proposal records the UX route

- GIVEN an accepted proposal affects a visual interface
- WHEN the Product Owner completes proposal capture
- THEN the applicability decision is `required: true` with a scope-backed
  reason
- AND the proposal routes to UX before architecture

#### Scenario: Nonvisual proposal records the direct route

- GIVEN an accepted proposal affects only CLI, API, framework, or
  specification behavior
- WHEN the Product Owner completes proposal capture
- THEN the applicability decision is `required: false` with a scope-backed
  reason
- AND the proposal routes directly to architecture without UX artifacts

#### Scenario: Applicability is missing or contradictory

- GIVEN a proposal lacks a valid or unique applicability decision
- WHEN the proposal handoff is evaluated
- THEN handoff remains blocked
- AND the Product Owner requests the clarification needed to resolve the
  decision

### Requirement: Proposal acceptance precedes downstream artifacts

A captured proposal MUST remain unaccepted until an identified approver accepts
the current proposal content. Changes that materially alter scope, scenarios,
acceptance criteria, or applicability MUST require renewed acceptance before
UX or architecture begins.

#### Scenario: Current proposal is accepted

- GIVEN an identified requester or maintainer approves the current proposal
- WHEN the Product Owner evaluates handoff readiness
- THEN the accepted revision is recorded as the basis for downstream work
- AND the applicable UX or architecture handoff may begin

#### Scenario: Proposal changes after acceptance

- GIVEN a proposal was accepted and then changed materially
- WHEN the next handoff is evaluated
- THEN the previous acceptance does not satisfy the current revision
- AND the Product Owner obtains renewed acceptance before progression

#### Scenario: Capture decision is not proposal acceptance

- GIVEN a requester authorizes repository capture of a planning artifact
- WHEN the proposal is created
- THEN capture proceeds without treating the authorization as approval
- AND implementation remains blocked until the current proposal is accepted
