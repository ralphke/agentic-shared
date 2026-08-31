---
name: openspec-propose
description: Create a complete OpenSpec change plan from a feature or fix request. Use when the user wants a proposal, delta specs, design, and tasks ready for review. Do not use for implementation.
allowed-tools: Bash(openspec:*)
license: MIT
compatibility: Requires Node.js 26 or later and the OpenSpec CLI.
metadata:
  author: agentic-shared
  upstream: Fission-AI/OpenSpec
  version: "1.0"
---

# OpenSpec Proposal

## Prerequisites

Before changing artifacts, confirm `openspec --version` and `openspec context --json`
succeed. If either fails, stop without writing files and report:

```powershell
npm install -g @fission-ai/openspec@latest
openspec init
openspec context --json
```

Node.js 26 or later is required. Do not fall back to a legacy prompt workflow.

## Workflow

1. Obtain a clear change description from either a GitHub issue labelled `idea` or a
   direct user request. When an issue is supplied, read its title, form fields, labels,
   and discussion as the Product Owner input and retain its number in the proposal.
2. Direct `/opsx:propose <description>` invocation is a valid alternative and does not
   require a GitHub issue. Ask only about ambiguity that changes scope, compatibility,
   or acceptance criteria.
3. Derive a kebab-case name unless one was supplied.
4. Run `openspec new change "<name>"`, using an explicitly requested schema only.
5. Run `openspec status --change "<name>" --json` and determine the full transitive
   artifact set required by `applyRequires` and artifact dependencies.
6. For each ready required artifact, run
   `openspec instructions <artifact-id> --change "<name>" --json`, read completed
   dependencies, and create the artifact at the returned resolved output path.
7. Re-run status after each artifact until every required artifact is done or skipped.
8. Ensure proposals identify legal/IP risk. Legal-risk changes require the Software
   Fabric legal-review gate before code review or deployment.
9. Link the proposal from the idea issue and retain `idea` and `stage:proposal` labels
   until planning is approved. Present the artifacts for review and stop.

## Guardrails

- This skill authorizes planning only. Do not edit project code or begin apply work.
- Follow CLI-provided paths, templates, and artifact instructions; do not assume paths.
- Create specifications as deltas, never by editing source-of-truth specs directly.
- If the change already exists, ask whether to continue it or create a different change.

## Output

Report the change name, created artifact paths, skipped conditional artifacts, and the
next command: `/openspec-apply-change <name>` after explicit user approval.