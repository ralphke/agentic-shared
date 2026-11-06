# Delta for testing-standards

## ADDED Requirements

### Requirement: Applicable UX Criterion Validation

For changes affecting a visual interface, QA MUST map every UX criterion to a
test or documented validation check and record the actual result and evidence.
Applicable checks MUST cover interaction states, accessibility, responsive
behavior, keyboard, and touch. Excluded dimensions MUST have scope-backed
reasons; unavailable required checks MUST remain unresolved.

#### Scenario: Visual criteria have traceable validation

- GIVEN a visual brief contains stable criterion IDs
- WHEN QA validates the implementation
- THEN each ID maps to an identified test or documented check
- AND the result and supporting evidence are recorded
- AND applicable loading, empty, success, failure, and recovery behavior is
  included

#### Scenario: Accessibility and responsive coverage is explicit

- GIVEN a visual change has applicable accessibility and form-factor criteria
- WHEN QA records validation
- THEN results address keyboard and focus, semantics and labels, contrast and
  non-color cues, zoom or reflow, error communication, reduced motion, and touch
  as applicable
- AND desktop, tablet, and mobile expectations are checked where applicable
- AND emulation is distinguished from real-device validation

#### Scenario: Inapplicable dimension is explained

- GIVEN touch or a form factor is outside the accepted affected experience
- WHEN QA records its validation plan
- THEN the excluded dimension has a scope-backed reason
- AND the reason is not presented as a passing device check

#### Scenario: Unavailable validation does not become a pass

- GIVEN a required check cannot be performed
- WHEN QA reports results
- THEN it records the missing coverage and blocker
- AND does not claim that criterion passed or complete the UX gate

### Requirement: Nonvisual Changes Have No UX Testing Obligations

CLI-only, API-only, framework, and other changes with no affected visual
interface MUST NOT require UX briefs, UX-specific specs, UX validation
reports, UX tests, or frontend tooling. Their functional scenario tests,
negative tests, coverage obligations, and existing mandatory quality gates
MUST remain required.

#### Scenario: CLI tests run without UX artifacts

- GIVEN a CLI-only proposal records nonvisual applicability
- WHEN QA validates commands, output, and failures from functional scenarios
- THEN no UX artifact, UX test, browser, or device check is required
- AND normal functional tests and quality gates still run

#### Scenario: API framework tests run without UX artifacts

- GIVEN an API-only or framework proposal affects no visual interface
- WHEN QA validates contracts, error handling, and relevant security behavior
- THEN the absence of UX specs, briefs, and reports does not block testing
- AND functional and coverage gates are not weakened

#### Scenario: Mixed changes preserve both testing responsibilities

- GIVEN a change affects a visual surface and an API
- WHEN QA maps test coverage
- THEN visual criteria receive applicable UX validation
- AND API contracts receive ordinary functional tests without new UX duties

### Requirement: Applicable UX Evidence Gates Test Completion

For visual changes, automated stage gates MUST reject missing or incomplete
criterion mappings, failed required checks, and absent supporting evidence
before test completion or security entry. Configured consumer UX automation
MUST pass; recorded coverage percentages alone MUST NOT satisfy this gate.
Nonvisual changes MUST bypass only these UX obligations.

#### Scenario: Coverage cannot substitute for UX evidence

- GIVEN code coverage passes but a visual criterion has no validation evidence
- WHEN test completion or security entry is evaluated
- THEN the UX gate fails with the missing criterion identified
- AND the change is not reported UX-validated

#### Scenario: Configured UX automation fails

- GIVEN a visual consumer has configured required automated UX checks
- WHEN a required check fails or has no successful result for the evaluated
  revision
- THEN test completion remains blocked
- AND a self-reported passing result cannot replace the failed automation

#### Scenario: Complete applicable evidence permits progression

- GIVEN every visual criterion has passing evidence and configured UX checks
  pass
- WHEN test completion is evaluated
- THEN the UX gate passes without claiming checks not performed
- AND ordinary tests, coverage, security, and other mandatory gates remain
  independently required

#### Scenario: Nonvisual route requires no UX runner configuration

- GIVEN accepted applicability records a CLI-only or API-only change
- WHEN its stage gates run
- THEN missing UX reports and UX runner configuration are not errors
- AND the normal functional test command still runs
