---
name: software-fabric-kickoff
description: Start a Software Fabric workflow from a raw idea and coordinate OpenSpec planning. Use when the user wants to begin a complete SDLC workflow. Do not use to bypass planning approval or resume a specific implementation task.
allowed-tools: Bash(openspec:*)
license: MIT
compatibility: Requires Node.js 26 or later and the OpenSpec CLI.
metadata:
  author: agentic-shared
  version: "1.0"
---

# Software Fabric Kickoff

## Prerequisites

Confirm `openspec --version` and `openspec context --json` before invoking any workflow
action. If unavailable, stop without changing artifacts or code and provide:

```powershell
npm install -g @fission-ai/openspec@latest
openspec init
openspec context --json
```

Node.js 26 or later is required. Do not fall back to legacy prompt behavior.

## Workflow

1. Obtain the user's idea and invoke `openspec-propose` to create all planning artifacts.
2. Confirm the proposal identifies scope, scenarios, acceptance criteria, and applicable
   legal/IP risk.
3. Present the proposal, delta specs, design, and tasks for human approval.
4. Stop after planning. A request to start the kickoff authorizes planning only, even when
   it also asks for implementation.
5. After the user makes a new explicit request, invoke `openspec-apply-change` for the
   selected change.
6. When implementation and tests are complete, invoke `openspec-verify-change`.
7. Require tests, coverage, security, conditional legal approval, code review, and CI
   gates before archive.

## Guardrails

- Keep Product Owner, Architect, Developer, QA, Security, Legal, and Reviewer handoffs
  traceable through the change artifacts and stage labels.
- Do not implement code during kickoff.
- Do not treat a proposal review as implementation approval.
- Do not archive while a mandatory Software Fabric gate is incomplete.

## Output

Report the change name, planning artifacts created, approval status, and the next skill to
invoke. After planning, prompt the user to explicitly request apply work.