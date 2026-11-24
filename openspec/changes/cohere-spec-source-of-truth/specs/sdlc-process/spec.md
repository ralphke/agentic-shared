# Delta for sdlc-process

## MODIFIED Requirements

### Requirement: Delta reconciliation preserves or intentionally retires scenarios

Before a `MODIFIED` delta is applied, every scenario in the current requirement
MUST be evaluated. A still-relevant scenario MUST be preserved or updated in the
delta; an intentionally retired scenario MUST have a recorded reason and
migration or replacement. A stale `ADDED` requirement MUST be reconciled with
the existing canonical requirement rather than added again.

#### Scenario: Existing scenario remains relevant

- GIVEN a current scenario is omitted from a `MODIFIED` requirement
- WHEN the delta is reconciled
- THEN the scenario is evaluated against the accepted change
- AND a still-relevant scenario is restored or updated in the delta

#### Scenario: Existing scenario is no longer relevant

- GIVEN a current scenario no longer applies to the accepted behavior
- WHEN the delta is reconciled
- THEN its retirement is explicit
- AND the record identifies the reason and the replacement or migration

#### Scenario: Active delta attempts to add an existing requirement

- GIVEN a completed active change has an `ADDED` requirement already
  present in the canonical spec
- WHEN archive readiness is evaluated
- THEN the delta is reconciled as retained or modified canonical behavior
- AND no duplicate requirement is introduced

### Requirement: Handoff disputes use accountable collaboration

When stage responsibilities overlap, the current stage owner MUST identify the
primary accountable role, contributing roles, shared evidence, and the proposed
next-stage decision. A legitimate overlap MUST NOT be treated as a failure by
itself; unresolved disagreement MUST block handoff until the architect or a
responsible human maintainer records a common-ground resolution.

#### Scenario: Overlap has an agreed primary owner

- GIVEN two personas contribute to the same handoff activity
- WHEN the stage owner prepares the handoff
- THEN the handoff records one accountable role and the named contributors
- AND the work proceeds after the required evidence is complete

#### Scenario: Overlap remains disputed

- GIVEN collaborating personas disagree about ownership or exit criteria
- WHEN the current stage tries to advance
- THEN the handoff is blocked
- AND the disagreement is escalated with the competing interpretations and
  the minimum evidence needed for a common-ground resolution

#### Scenario: Shared ownership does not weaken gate ownership

- GIVEN multiple roles contribute to a requirement or artifact
- WHEN a mandatory gate is evaluated
- THEN the gate remains owned by its responsible quality role
- AND shared contribution does not transfer, waive, or self-approve the gate

### Requirement: Archive readiness requires complete current evidence

A change MUST NOT archive until the current revision has complete required
planning artifacts and acceptance, all tasks complete, passing scenario tests,
no remaining removed-reference behavior, strict OpenSpec validation, green CI,
at least 80% new-code coverage, no HIGH or CRITICAL security findings, code
review approval, all acceptance criteria, applicable legal approval, and
applicable operational evidence. Missing or unusable evidence MUST remain
unverified and blocking.

#### Scenario: All applicable archive evidence is current

- GIVEN all required evidence is current for the evaluated revision
- WHEN archive readiness is checked
- THEN every mandatory gate is recorded as passed
- AND delta synchronization and archive may proceed

#### Scenario: A mandatory gate lacks evidence

- GIVEN one applicable gate has no current usable evidence
- WHEN archive readiness is checked
- THEN the gate remains unverified
- AND no synchronization, move, or archive action is performed

#### Scenario: Non-applicability is justified by scope

- GIVEN a mandatory-looking gate does not apply to the accepted scope
- WHEN archive readiness is checked
- THEN the scope-based reason is recorded
- AND all other mandatory gates remain independently required

#### Scenario: Active change cannot archive because its delta is stale

- GIVEN a completed active change has a delta that conflicts with the
  canonical spec
- WHEN archive readiness is checked
- THEN the change remains active
- AND reconciliation is required before sync or archive
