# Testing Standards — Source of Truth

> **Domain:** `testing-standards` | **Owner:** qa-engineer  
> Defines the testing strategy, required test types, coverage minimums, and
> quality gates for all Software Fabric changes.

---

## Purpose

Defines scenario-driven testing, coverage, determinism, and CI quality-gate
requirements for every change.

## Overview

Every change MUST include automated tests before it can pass the quality gate.
Tests are generated from OpenSPEC Given/When/Then scenarios and validated in CI.
The QA Engineer Agent owns test generation and coverage.
For affected visual interfaces, QA also validates stable UX criteria and
records evidence; unavailable required checks block progression. Nonvisual
CLI/API/framework changes require no UX artifacts or frontend tooling, while
ordinary functional testing and coverage remain mandatory.

---

## Requirements

### Requirement: Scenario-Driven Test Generation

Every Given/When/Then scenario in `spec.md` MUST have at least one corresponding
test.

**Test mapping:**

- `GIVEN` → test setup / preconditions
- `WHEN` → test action
- `THEN` → assertion

#### Scenario: Each spec scenario maps to a test

- GIVEN a spec with 5 Given/When/Then scenarios
- WHEN the QA Engineer Agent generates tests
- THEN ≥ 5 test functions exist, one per scenario
- AND each test is named to reflect its scenario (e.g.,
  `test_empty_export_returns_204`)

#### Scenario: Unhappy path scenarios generate negative tests

- GIVEN a spec scenario with a `WHEN` condition that should produce an error
- WHEN the QA Agent generates the test
- THEN the test asserts the error response (exception, status code, error
  message)

---

### Requirement: Test Pyramid Compliance

Changes MUST include tests at multiple levels following the test pyramid.

**Test levels and requirements:**

| Level       | Scope                      | Required When                          | Coverage Goal          |
| ----------- | -------------------------- | -------------------------------------- | ---------------------- |
| Unit        | Single function/class      | Any new function or method             | ≥ 90% of units         |
| Integration | Component interaction      | New service calls, DB queries, APIs    | All integrations       |
| End-to-End  | Full user journey          | User-facing features or flows          | Happy path + 1 unhappy |
| Performance | Latency / throughput       | New endpoints or data-heavy operations | p99 baseline           |
| Smoke       | Critical paths post-deploy | Every deployment                       | All P0 paths           |

#### Scenario: New API endpoint triggers integration test

- GIVEN a new REST endpoint `POST /api/v1/exports`
- WHEN the QA Agent determines test requirements
- THEN an integration test is written that calls the endpoint via HTTP
- AND tests cover: success (201), validation error (400), auth failure (401),
  not found (404)

#### Scenario: User-facing feature triggers e2e test

- GIVEN a new "Export to CSV" button on the UI
- WHEN the QA Agent determines test requirements
- THEN an e2e test (Playwright/Selenium) covers the full user journey
- AND the test runs headlessly in CI

---

### Requirement: Code Coverage Floor

New code MUST achieve ≥ 80% line coverage. Existing code MUST NOT regress below
its current baseline.

#### Scenario: Coverage gate passes

- GIVEN a PR where all new code is ≥ 80% covered
- WHEN the coverage report is generated
- THEN the CI coverage gate passes
- AND a coverage badge comment is added to the PR showing new vs. baseline

#### Scenario: Coverage regression is blocked

- GIVEN a PR where new code drops coverage from 85% to 72%
- WHEN the CI coverage check runs
- THEN the PR is labelled `coverage-insufficient`
- AND the uncovered lines are listed in a comment
- AND the merge is blocked until coverage is restored

---

### Requirement: Test Determinism

All automated tests MUST be deterministic — no flaky tests are allowed in the CI
pipeline.

**Anti-patterns to prevent:**

- Tests that depend on wall-clock time (use clock mocking)
- Tests that depend on external services without mocking
- Tests with global state that leaks between test runs
- Tests that produce different results on different OS/arch

#### Scenario: Flaky test is quarantined

- GIVEN a test that fails intermittently in CI
- WHEN it fails 3+ times without code changes
- THEN it is moved to a quarantine suite and an issue is opened to fix it
- AND it does NOT block the main CI pipeline while quarantined

---

### Requirement: Test Documentation

Tests MUST be self-documenting — readable as executable specifications.

**Requirements:**

- Test names MUST describe the scenario: `test_<subject>_<when>_<expected>`
- AAA pattern: Arrange / Act / Assert with blank lines between sections
- No magic numbers — use named constants or fixtures
- Complex assertions MUST include a failure message explaining what was expected

#### Scenario: Test name communicates intent

- GIVEN a test for password validation
- WHEN the test is named
  `test_password_validator_with_short_password_returns_false`
- THEN a reader understands the test without reading the body

---

### Requirement: CI Test Execution

All tests MUST run automatically in the GitHub Actions CI pipeline on every PR.

**CI test requirements:**

- Tests run on PR opened, synchronized, and reopened events
- Tests run in a clean, isolated environment (no shared state between PRs)
- Test results are reported as GitHub Check Runs with pass/fail per test
- Test failures produce a summary comment on the PR listing failing tests
- Test run duration MUST not exceed 15 minutes for the full suite

#### Scenario: PR test run reports results

- GIVEN a PR with 3 failing tests out of 50
- WHEN the CI pipeline runs
- THEN a GitHub Check Run is marked "failure"
- AND a PR comment lists the 3 failing tests with error messages
- AND the merge is blocked until tests pass

---

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
