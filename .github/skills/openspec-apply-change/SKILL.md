---
name: openspec-apply-change
description: Implement pending tasks from an approved OpenSpec change. Use when the user asks to start or continue implementation. Do not use to create planning artifacts or verify a change.
allowed-tools: Bash(openspec:*)
license: MIT
compatibility: Requires Node.js 26 or later and the OpenSpec CLI.
metadata:
  author: agentic-shared
  upstream: Fission-AI/OpenSpec
  version: "1.0"
---

# OpenSpec Apply Change

## Prerequisites

Run `openspec --version` and `openspec context --json` first. If unavailable, stop
without modifying artifacts or code and provide the installation and initialization
commands in the proposal skill's prerequisite section. Do not use legacy prompts.
Do not fall back to legacy prompts.

## Workflow

1. Select the named change, infer it from an unambiguous conversation, or run
   `openspec list --json` and ask the user to choose.
2. Run `openspec status --change "<name>" --json`.
3. Run `openspec instructions apply --change "<name>" --json`.
4. If the state is blocked, report the missing artifacts and stop. If all tasks are done,
   report that the change is ready for verification or archive.
5. Read every file in `contextFiles`, including proposal, delta specs, design, and tasks.
6. Implement each pending task in order. Keep changes within approved scope and update a
   task checkbox only after its behavior is complete.
7. Run the narrowest relevant tests after each meaningful change and the project test
   suite before reporting implementation complete.
8. Route completed work to QA, then security review, conditional legal review, and code
   review according to Software Fabric gates.

## Guardrails

- Treat CLI status, instructions, and context files as authoritative.
- Pause for unclear tasks, design conflicts, scope expansion, or failed validation.
- Do not mark partial or deferred work complete.
- Do not bypass testing, security, legal, or review gates.

## Output

Report selected change, task progress, completed tasks, validations run, and any blocker.