---
name: openspec-verify-change
description: Verify an OpenSpec change is complete, correctly implemented, and ready for archive. Use before archive when the user requests validation. Do not implement incomplete tasks or bypass mandatory gates.
allowed-tools: Bash(openspec:*)
license: MIT
compatibility: Requires Node.js 26 or later and the OpenSpec CLI.
metadata:
  author: agentic-shared
  upstream: Fission-AI/OpenSpec
  version: "1.0"
---

# OpenSpec Verify Change

**Store selection:** If the user names a store (a store is a standalone OpenSpec repo
registered on this machine) or the work lives in one, run `openspec store list --json`
to discover registered store ids, then pass `--store <id>` on every OpenSpec command
that reads or writes specs and changes (`status`, `instructions`, `list`, `show`,
`validate`, `archive`, `doctor`, `context`, `schemas`, `view`). Once selected, treat
`--store <id>` as sticky for the rest of the workflow. Without a store, commands act
on the nearest local `openspec/` root.

## Prerequisites

Run `openspec --version` and `openspec context --json` before inspection. If either
fails, stop with no artifact changes and provide the standard Node.js 26+ installation
and initialization commands. Never fall back to legacy prompts.

## Workflow

1. Select the named or unambiguous active change; otherwise run `openspec list --json`
   and ask the user to choose.
2. Run `openspec status --change "<name>" --json` and
   `openspec instructions apply --change "<name>" --json`.
3. Read all available CLI-provided context files.
4. Report completeness: completed tasks and implementation evidence for every delta
   requirement.
5. Report correctness: implementation and test coverage for every spec scenario.
6. Report coherence: adherence to design decisions and established project patterns.
7. Enforce Software Fabric gates: tests passing, 80% new-code coverage, no HIGH or
   CRITICAL security findings, required legal approval for legal-risk changes, code-review
   approval, and complete acceptance criteria.
8. Run `openspec validate --change "<name>"` when the installed CLI supports it. Report
   unsupported validation as a warning, not a successful gate.

## Severity

- **CRITICAL:** incomplete task, unimplemented requirement, failed mandatory gate, or
  missing required legal approval. Block archive.
- **WARNING:** missing scenario coverage or likely design divergence. Remediate before
  archive unless explicitly accepted by the responsible owner.
- **SUGGESTION:** non-blocking pattern improvement.

## Output

Provide a completeness, correctness, and coherence scorecard; list actionable findings
by severity; name skipped checks and why; then state whether the change is ready for
archive.

## When to Use & Triggers

Use after implementation when pre-archive validation is requested. Do not implement incomplete work.

## Workflows & Steps

1. Inspect tasks, artifacts, implementation, and scenario coverage.
2. Run available quality gates and classify findings.
3. Report archive readiness with evidence.

## Scripts & Tools

- Run OpenSpec status, validation, tests, coverage, security, CI, and review checks as available.
- Inspect implementation against every scenario and task.

## Rules & Guidelines

- Block archive on incomplete tasks, failed mandatory gates, missing legal approval, or coverage below 80%.
- Distinguish blocking findings from warnings and suggestions.

## Error Handling

| Error | Cause | Fix |
|---|---|---|
| Missing evidence | A required check was not run | Mark it skipped and report it as blocking |
| Scenario mismatch | Implementation diverges from the spec | Return to implementation and repair it |
| Gate failure | A required quality gate failed | Keep the change out of archive until resolved |

## Scenarios & References

- Use proposal, design, delta specs, tasks, test results, security results, and CI status.
- Confirm removed requirements are no longer referenced.

## Quick Reference

| Task | Result |
|---|---|
| Check completeness | All tasks and scenarios are covered |
| Check gates | Tests, coverage, security, review, CI, and legal conditions pass |
| Decide | Ready for archive or actionable findings |

## Collaboration & Iteration Loop

- Return findings to the responsible persona, then rerun verification after remediation.

## Output Specs, Success, Evaluation & Security

- Output scorecard, severity-ordered findings, skipped checks, and archive readiness.
- Success requires reproducible evidence and no unresolved security or legal exposure.