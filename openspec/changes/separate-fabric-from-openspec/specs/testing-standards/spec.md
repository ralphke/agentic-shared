# Delta for testing-standards

## ADDED Requirements

### Requirement: Explicit OpenSpec Compatibility

The Fabric integration MUST declare its supported OpenSpec versions and test
each declared version. Unsupported versions MUST be identified without a
success-shaped compatibility result.

#### Scenario: Supported version is tested

- GIVEN a declared supported OpenSpec version
- WHEN the compatibility suite runs
- THEN it tests the upstream and Fabric integration against that version
- AND reports the version and test outcome

#### Scenario: Unsupported version is detected

- GIVEN an OpenSpec version outside the declared supported set
- WHEN the compatibility check runs
- THEN it reports the unsupported version
- AND does not claim that compatibility was verified

#### Scenario: Upstream changes are reviewed before adoption

- GIVEN a proposed OpenSpec version update
- WHEN the supported set is expanded
- THEN upstream skill changes are reviewed
- AND compatibility tests pass for each newly supported version

### Requirement: Fabric Gate Evidence Validation

Tests MUST verify the Fabric gate evidence contract, including revision
binding, applicability, trusted sources, and failure handling.

#### Scenario: Valid current evidence passes

- GIVEN all applicable evidence is current, trusted, and passing
- WHEN the corresponding gate is evaluated
- THEN the evaluation reports success for the evaluated revision

#### Scenario: Missing or stale evidence fails

- GIVEN required evidence is missing, malformed, or for another revision
- WHEN the corresponding gate is evaluated
- THEN the evaluation fails and identifies the unsatisfied evidence
- AND does not substitute a warning or default success

#### Scenario: Untrusted passing claim fails

- GIVEN a passing gate claim without an authorized evidence source
- WHEN the corresponding gate is evaluated
- THEN the evaluation rejects the claim
- AND the affected control remains blocked

#### Scenario: Trusted different-revision mapping passes

- GIVEN a fresh authorized mapping explicitly binds the change identity,
  evaluated and deployed revisions, and verified release and deployment records
- WHEN archive evidence is evaluated
- THEN change gates are checked against the evaluated revision
- AND operational gates are checked against the deployed revision
- AND the verified same-revision path continues to work

#### Scenario: Invalid or superseded revision mapping fails

- GIVEN a different-revision mapping is missing, duplicated, stale,
  unauthorized, or inconsistent with the current release/tag/deployment status
- WHEN archive evidence is evaluated
- THEN the control fails before spec writes or archive moves
- AND neither ancestry nor an author-supplied mapping grants approval

### Requirement: Skill Boundary Quality Comparison

Affected representative skills and instructions MUST be assessed before and
after the change using the same clarity, structure, execution-guidance, and
handoff-quality rubric.

#### Scenario: Quality evidence is reproducible

- GIVEN representative affected skills and instructions
- WHEN their baseline and changed versions are evaluated
- THEN both use the same documented rubric
- AND the results and differences are recorded
