# Design: Add Chronicle Retrospective Follow-Up

## Decision

Add non-executable follow-up guidance to the Workflow Improvement Loop issue
report. GitHub Actions will continue to analyze only repository issues and pull
requests; maintainers may optionally run Chronicle in VS Code for local session
and cost analysis.

## Rationale

Chronicle accesses the developer's Copilot session store through VS Code, which
is not available to a scheduled GitHub Actions runner. Keeping the commands as
instructions preserves privacy and avoids placing personal chat or token data in
the workflow report.

## Validation

Parse the workflow YAML and confirm the generated report includes the two
Chronicle command references and the local, voluntary data boundary.
