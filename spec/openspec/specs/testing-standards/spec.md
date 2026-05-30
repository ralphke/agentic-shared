# Testing Standards — Source of Truth

> **Domain:** `testing-standards` | **Owner:** qa-engineer  
> Defines the testing strategy, required test types, coverage minimums,
> and quality gates for all Software Fabric changes.

---

## Overview

Every change MUST include automated tests before it can pass the quality
gate. Tests are generated from OpenSPEC Given/When/Then scenarios and
validated in CI. The QA Engineer Agent owns test generation and coverage.

---

## Requirements

### Requirement: Scenario-Driven Test Generation
Every Given/When/Then scenario in `spec.md` MUST have at least one corresponding test.

**Test mapping:**
- `GIVEN` → test setup / preconditions
- `WHEN` → test action
- `THEN` → assertion

#### Scenario: Each spec scenario maps to a test
- GIVEN a spec with 5 Given/When/Then scenarios
- WHEN the QA Engineer Agent generates tests
- THEN ≥ 5 test functions exist, one per scenario
- AND each test is named to reflect its scenario (e.g., `test_empty_export_returns_204`)

#### Scenario: Unhappy path scenarios generate negative tests
- GIVEN a spec scenario with a `WHEN` condition that should produce an error
- WHEN the QA Agent generates the test
- THEN the test asserts the error response (exception, status code, error message)

---

### Requirement: Test Pyramid Compliance
Changes MUST include tests at multiple levels following the test pyramid.

**Test levels and requirements:**
| Level         | Scope                          | Required When                          | Coverage Goal |
|---------------|--------------------------------|----------------------------------------|---------------|
| Unit          | Single function/class          | Any new function or method             | ≥ 90% of units|
| Integration   | Component interaction          | New service calls, DB queries, APIs    | All integrations|
| End-to-End    | Full user journey              | User-facing features or flows          | Happy path + 1 unhappy|
| Performance   | Latency / throughput           | New endpoints or data-heavy operations | p99 baseline  |
| Smoke         | Critical paths post-deploy     | Every deployment                       | All P0 paths  |

#### Scenario: New API endpoint triggers integration test
- GIVEN a new REST endpoint `POST /api/v1/exports`
- WHEN the QA Agent determines test requirements
- THEN an integration test is written that calls the endpoint via HTTP
- AND tests cover: success (201), validation error (400), auth failure (401), not found (404)

#### Scenario: User-facing feature triggers e2e test
- GIVEN a new "Export to CSV" button on the UI
- WHEN the QA Agent determines test requirements
- THEN an e2e test (Playwright/Selenium) covers the full user journey
- AND the test runs headlessly in CI

---

### Requirement: Code Coverage Floor
New code MUST achieve ≥ 80% line coverage. Existing code MUST NOT regress below its current baseline.

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
All automated tests MUST be deterministic — no flaky tests are allowed in the CI pipeline.

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
- WHEN the test is named `test_password_validator_with_short_password_returns_false`
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
