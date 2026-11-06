---
name: test-generation
description:
  Generate deterministic tests mapped to OpenSpec scenarios with explicit
  coverage evidence. Use for the test stage after implementation. Do not use as
  a replacement for exploratory QA or security-gate approval.
---

# Skill: Test Generation from Spec Scenarios

**Persona:** QA Engineer Agent **Input:** `spec.md` scenarios + source code from
Developer Agent **Output:** Test suites with ≥ 80% coverage on new code

Read `## UX Applicability` in the accepted proposal first. Missing or conflicting
scope requires clarification. CLI-only, API-only, and framework changes with no
affected visual interface require no UX artifacts, UX-specific specs, UX tests,
or frontend tooling. Their functional specs, tests, and quality gates remain.
For visual changes only, also consume `ux-brief.md` and produce criterion-level
validation evidence.

---

## When to Use This Skill

Use when a PR is labelled `stage:test` by the Developer Agent.

---

## Execution Steps

1. **Read spec scenarios** — Open
   `openspec/changes/<slug>/specs/<domain>/spec.md`
2. **List all scenarios** — Enumerate every Given/When/Then block
3. **Inspect source code** — Understand the implementation to determine test
   levels
4. **Plan test coverage** — Map scenarios to test level (unit/integration/e2e)
   and, for visual changes only, map every stable UX criterion ID to a test or
   documented check. Cover applicable states, WCAG 2.2 AA behavior, responsive
   desktop/tablet/mobile layouts, keyboard/focus, and touch. Explain excluded
   dimensions and distinguish real devices from emulation.
5. **Write tests** — One test function per scenario using project test framework
6. **Add AI failure pattern tests** — Explicitly add tests for patterns common
   in AI-generated code that may not appear in spec scenarios:
   - Auth check bypassed or absent (test that unauthenticated requests are
     rejected)
   - Inverted auth condition (test that access is denied, not just that it
     returns something)
   - Missing null/empty-input handling (test with null, empty string, empty
     list)
   - Happy-path-only error handling (test that errors propagate, not silently
     swallow)
7. **Add edge cases** — Add boundary tests for numeric limits, empty inputs,
   large inputs
8. **Mock externals** — Mock all HTTP calls, database queries, file I/O
9. **Run tests** — Execute test suite and capture coverage report
10. **Fill gaps** — Add targeted tests for uncovered lines (≥ 80% required)
11. **Label PR** — Apply `stage:security` only after functional gates and
    applicable UX validation pass. Unavailable required checks remain blocked,
    not passed; code coverage alone cannot prove UX quality.

---

## Test Naming Convention

```text
test_<subject>_<condition>_<expected_outcome>

# Python examples:
test_export_service_with_valid_user_returns_csv_response
test_export_service_with_unknown_user_raises_not_found_error
test_export_service_with_empty_dataset_returns_empty_csv

# .NET examples:
ExportToCsv_WithValidUser_ReturnsCsvContent
ExportToCsv_WithUnknownUser_ThrowsUserNotFoundException
ExportToCsv_WithEmptyDataset_ReturnsEmptyCsv
```

---

## Test Level Decision Matrix

| Code Type                          | Unit | Integration | E2E |
| ---------------------------------- | ---- | ----------- | --- |
| Pure function / utility            | ✅   |             |     |
| Service with injected dependencies | ✅   | ✅          |     |
| API endpoint handler               |      | ✅          |     |
| User-facing workflow               |      |             | ✅  |
| Database query                     |      | ✅          |     |
| Auth/authorization logic           | ✅   | ✅          |     |

---

## Quality Checks

- [ ] ≥ 1 test per Given/When/Then scenario
- [ ] All unhappy paths have negative tests
- [ ] AI failure pattern tests present (auth bypass, inverted auth, null inputs,
      swallowed errors)
- [ ] All external dependencies are mocked in unit tests
- [ ] Coverage report shows ≥ 80% for new code
- [ ] Test names describe the scenario without reading the body
- [ ] No `time.sleep()` or wall-clock dependencies
- [ ] Tests pass deterministically (run 3x to verify)
- [ ] Tests run in < 30s for unit suite, < 5min for integration suite
- [ ] For visual changes, each UX criterion has a result and evidence; required
      consumer UX automation passes for the evaluated revision
- [ ] Nonvisual changes require no UX report, runner, or device checks

---

## Collaboration & Iteration Loop

- Incorporate recurring defect patterns from recent PR/issue history into
  regression tests.
- If history is sparse, seed baseline negative tests for auth, null-input, and
  error propagation paths.
- Publish flaky/failing-pattern insights for downstream skill and workflow
  updates.

## Scripts & Tools

The shared helper travels with this skill. Validate a handoff locally:

```powershell
python .github/skills/test-generation/scripts/validate_ux_gate.py openspec/changes/<slug> --phase design
```

Use phase `ux` for proposal entry, `design` or `test` for applicable brief
checks. Nonvisual changes require only their proposal decision, never UX files.

### Visual evidence and consumer CI

Only visual changes create `ux-validation.json` in their change directory:

```json
{
  "criteria": [
    {
      "id": "UX-01",
      "method": "automated",
      "result": "passed",
      "evidence": "https://github.com/owner/repo/actions/runs/123"
    }
  ]
}
```

List every brief criterion exactly once. `method` is `automated` or `manual`;
`result` is `passed`, `failed`, or `blocked`. Evidence must identify the actual
test result or documented check. A required unavailable check stays blocked.
Record device versus emulated coverage in that evidence; non-applicable
dimensions need scope-backed reasons in the accepted brief.

Configure the trusted repository variable `UX_CHECK_NAMES`, for example
`["Browser UX", "Accessibility"]`, with unique check-run names produced by
consumer-owned CI. Those workflows execute the consumer's existing UX suites
on PR updates. Do not select an orchestrator gate itself or install a browser
stack merely for nonvisual work.

Phase `complete` or `security` checks the report and requires those checks to
succeed for `--head <full-PR-head-SHA>` in `--repository <owner/repo>`.
The helper waits up to five minutes for pending checks, then fails explicitly.
It reads all check-run pages and rejects ambiguous names, stale revisions,
skips, failures, and missing evidence. Report completeness does not certify
manual conformance; QA and review still evaluate the referenced evidence.

- Run the repository test command and its coverage command for the detected
  language.
- Use deterministic fixtures, mocks, and the project's existing test utilities.

## Rules & Guidelines

- Map every Given/When/Then scenario to at least one test.
- Require at least 80% coverage for new code and keep tests independent of
  wall-clock timing.
- Do not mark the test gate complete while failures, flaky tests, or uncovered
  unhappy paths remain.

## Error Handling

| Error                | Cause                                        | Fix                                                  |
| -------------------- | -------------------------------------------- | ---------------------------------------------------- |
| Scenario has no test | Scenario was missed during enumeration       | Add a test and link it to the scenario               |
| Coverage below 80%   | New behavior is untested                     | Add focused tests for uncovered branches             |
| Flaky test           | Shared state, timing, or external dependency | Isolate state, control time, and mock the dependency |

## Scenarios & References

- Use the change delta spec and repository testing standards as authoritative
  references.
- Include happy, unhappy, authorization, validation, and dependency-failure
  scenarios where relevant.

## Quick Reference

| Task               | Check                                                             |
| ------------------ | ----------------------------------------------------------------- |
| Enumerate behavior | List all Given/When/Then scenarios                                |
| Add coverage       | Choose unit, integration, or end-to-end level per decision matrix |
| Prove readiness    | Run tests and coverage three times for determinism                |
