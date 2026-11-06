# Delta for sdlc-process

## ADDED Requirements

### Requirement: Scope-Based UX Applicability

Each accepted proposal MUST record whether its change affects a visual
interface and why. Nonvisual changes MUST proceed without UX design,
UX-specific specs, briefs, or tests. Missing, invalid, duplicate, or
contradictory decisions MUST block handoff rather than imply an exemption.
Applicability MUST be checked separately for each change in a PR.

#### Scenario: CLI-only or API-only scope needs no UX artifacts

- GIVEN a proposal records no affected visual interface with a scope rationale
- WHEN architecture and testing gates run
- THEN missing UX artifacts do not fail either gate
- AND functional planning, testing, coverage, and security rules remain intact

#### Scenario: Visual scope requires UX

- GIVEN a proposal records an affected visual interface
- WHEN the proposal is accepted
- THEN work is routed through UX before architecture
- AND applicability does not exempt other mandatory gates

#### Scenario: Missing or ambiguous applicability blocks routing

- GIVEN applicability is absent, invalid, duplicated, or contradictory
- WHEN a stage gate evaluates the change
- THEN it fails with the affected proposal and needed correction
- AND does not silently select either route

#### Scenario: One nonvisual change cannot exempt another visual change

- GIVEN a PR includes one nonvisual change and one visual change
- WHEN required artifacts are evaluated
- THEN the visual change still requires its own brief and validation evidence
- AND the nonvisual change needs neither artifact

#### Scenario: Backend work in a UI repository remains nonvisual

- GIVEN a change affects only an API and does not change visual behavior
- WHEN its applicability is assessed from the accepted scope
- THEN the mere presence of frontend files does not require UX
- AND an inaccurate applicability declaration must be corrected during review

## MODIFIED Requirements

### Requirement: Ordered Agent Handoffs

Each applicable stage MUST complete before the next begins, signalled by PR
labels. Visual changes MUST pass UX before architecture; nonvisual changes
MUST route directly to architecture. Legal-risk changes MUST pass conditional
legal review after security and before review. A `legal:blocked` change MUST
NOT advance to review or deployment.

| Stage Label       | Responsible Persona | Next Stage                      |
| ----------------- | ------------------- | ------------------------------- |
| `stage:proposal`  | Product Owner       | `stage:ux` or `stage:design`    |
| `stage:ux`        | UX Designer         | `stage:design`                  |
| `stage:design`    | Architect           | `stage:implement`               |
| `stage:implement` | Developer           | `stage:test`                    |
| `stage:test`      | QA Engineer         | `stage:security`                |
| `stage:security`  | Security Engineer   | `stage:legal` or `stage:review` |
| `stage:legal`     | Legal & Compliance  | `stage:review`                  |
| `stage:review`    | Code Reviewer       | `stage:deploy`                  |
| `stage:deploy`    | DevOps/SRE          | `stage:operate`                 |
| `stage:operate`   | Operations SRE      | `archived`                      |

#### Scenario: Stage label gates merge

- GIVEN a PR without the `stage:review` label
- WHEN a merge is attempted
- THEN merge is blocked by a branch protection rule
- AND a comment lists incomplete stages

#### Scenario: Proposal hands off to UX before architecture

- GIVEN an accepted proposal affects a visual interface
- WHEN the Product Owner completes the proposal stage
- THEN work is routed to `stage:ux`
- AND the Architect does not begin until the UX Designer has produced the brief
- AND the UX Designer hands the brief to the Architect at `stage:design`

#### Scenario: Missing UX brief blocks architecture

- GIVEN a visual change labelled `stage:design` without a UX brief
- WHEN the design-stage gate validates its required artifacts
- THEN the gate blocks the Architect handoff and reports the missing UX brief

#### Scenario: Nonvisual proposal bypasses UX work

- GIVEN accepted applicability records no affected visual interface
- WHEN the Product Owner hands off the proposal
- THEN work goes directly to `stage:design`
- AND no UX stage, brief, UX-specific spec, or UX test is required
- AND ordinary functional specs, tests, and other gates remain required

#### Scenario: UX criteria and security gate remain in downstream order

- GIVEN visual implementation includes UX acceptance criteria from the brief
- WHEN the change advances through testing and security
- THEN QA validates applicable responsive, keyboard, and touch behavior
- AND security passes before review or deployment

#### Scenario: Legal stage is required for high-risk work

- GIVEN a change identified as having legal-risk triggers
- WHEN security review completes
- THEN it is routed to `stage:legal` before review
- AND `stage:review` is rejected until `legal:approved` is recorded

#### Scenario: Legal block prevents deployment

- GIVEN a PR labelled `legal:blocked`
- WHEN `stage:deploy` is applied
- THEN the orchestrator fails the deployment gate
- AND the PR remains blocked pending remediation or counsel sign-off

#### Scenario: Proposal hands off to UX only when necessary

- GIVEN an accepted proposal affects a visual interface
- WHEN the Product Owner completes the proposal stage
- THEN work is routed to `stage:ux`
- AND the UX Designer hands the completed brief to `stage:design`

#### Scenario: Missing applicable UX brief blocks architecture

- GIVEN a visual change labelled `stage:design` without a completed brief
- WHEN the design gate checks artifacts
- THEN it blocks handoff and reports the missing or incomplete brief

#### Scenario: Nonvisual proposal hands off directly to architecture

- GIVEN accepted applicability records no affected visual interface
- WHEN the Product Owner completes the proposal stage
- THEN the next stage is `stage:design` without UX work
- AND a mistakenly applied `stage:ux` reports the correct route without
  demanding a UX artifact

#### Scenario: Applicable UX validation precedes security

- GIVEN implementation includes applicable visual UX criteria
- WHEN test completion or security entry is evaluated
- THEN required UX checks must pass with traceable evidence
- AND passing code coverage alone cannot satisfy UX validation
- AND security still precedes review and deployment

#### Scenario: Updated changes are checked again

- GIVEN a PR changes after applicability or UX evidence was checked
- WHEN its head is updated while a relevant stage is active
- THEN applicable gates evaluate the current artifacts again
- AND prior successful checks do not automatically satisfy changed scope
