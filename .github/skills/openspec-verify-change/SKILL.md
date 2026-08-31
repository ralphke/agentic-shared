---
name: openspec-verify-change
description: Verify an OpenSpec change is complete, correctly implemented, and ready for archive. Use when the user asks to validate implementation before archive. Do not use to implement incomplete tasks.
allowed-tools: Bash(openspec:*)
license: MIT
compatibility: Requires Node.js 26 or later and the OpenSpec CLI.
metadata:
  author: agentic-shared
  upstream: Fission-AI/OpenSpec
  version: "1.0"
---

# OpenSpec Verify Change

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