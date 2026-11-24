# Delta for personas

## MODIFIED Requirements

### Requirement: Every persona has a complete execution contract

Every stage and supporting persona requirement MUST define its primary
responsibilities, required inputs, outputs, trigger, handoff or non-handoff
behavior, blocking conditions, and agent file. The contract MUST identify which
evidence proves that the persona may hand work to the next responsible role.

#### Scenario: Product Owner contract is complete

- GIVEN the Product Owner receives a raw idea or product request
- WHEN its persona contract is evaluated
- THEN the contract names proposal creation, acceptance, UX applicability,
  backlog, input, output, trigger, blockers, and the UX or architecture handoff

#### Scenario: UX Designer contract is complete

- GIVEN the UX Designer receives a visual proposal
- WHEN its persona contract is evaluated
- THEN the contract names the accepted-proposal input, `ux-brief.md` output,
  UX trigger, validation evidence, blocker return path, and architecture handoff

#### Scenario: Supporting persona declares no stage handoff

- GIVEN a persona supports other stages without owning a PR label
- WHEN its contract is evaluated
- THEN the contract explicitly states that it has no stage handoff
- AND identifies the current stage owner that consumes its support

#### Scenario: Missing contract field blocks standards compliance

- GIVEN a persona requirement omits inputs, outputs, trigger, handoff, or
  evidence
- WHEN persona standards are validated
- THEN the persona is reported as incomplete
- AND the gap blocks the standards change until the contract is restored

### Requirement: Persona artifacts have a primary owner and permitted collaborators

Each artifact MUST identify one primary owner accountable for completion while
allowing justified collaboration from other personas. The Product Owner MUST own
proposal capture and acceptance; the Systems Architect MUST own delta specs,
technical design, and ordered tasks. UX and QA MAY contribute criteria and
evidence without taking ownership of the artifacts assigned to the Architect.

#### Scenario: Proposal and architecture ownership remain distinct

- GIVEN a Product Owner creates a proposal and an Architect begins design
- WHEN planning responsibilities are evaluated
- THEN the Product Owner remains accountable for current proposal content
  and acceptance
- AND the Architect remains accountable for delta specs, `design.md`, and
  ordered tasks

#### Scenario: Collaborator contributes without replacing owner

- GIVEN a UX Designer provides criteria and QA provides validation evidence
- WHEN the Architect authors the design and tasks
- THEN those contributions are incorporated with attribution
- AND the Architect retains accountability for the resulting design
  artifacts

#### Scenario: Shared activity needs a common-ground decision

- GIVEN two personas have legitimate ownership claims over one activity
- WHEN the boundary affects a handoff
- THEN they document the shared activity, primary accountable owner,
  collaborators, evidence, and remaining disagreement
- AND unresolved disagreement is escalated to the architect or responsible
  human maintainer instead of silently selecting an exclusive owner

### Requirement: Persona requirements use normative language

Every persona responsibility that controls progression or handoff MUST use
`MUST` or `SHALL` language. Descriptive prose MAY add context but MUST NOT
replace the normative obligation.

#### Scenario: Existing persona lacks normative language

- GIVEN a persona requirement describes a responsibility only in prose
- WHEN strict specification validation is performed
- THEN the requirement includes an explicit `MUST` or `SHALL` obligation
- AND the original responsibility remains represented

#### Scenario: Informational context remains non-gating

- GIVEN a persona requirement contains useful explanatory background
- WHEN the normative rule is added
- THEN the background remains as context
- AND only the explicit obligation is treated as a handoff gate
