---
name: software-fabric-kickoff
description: Start a Software Fabric workflow from a raw idea and coordinate OpenSpec planning. Use for a new end-to-end SDLC change. Do not bypass planning approval or resume a specific implementation task.
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

**Store selection:** If the work lives in a registered standalone OpenSpec store, run
`openspec store list --json` to discover its id and pass `--store <id>` on every
applicable OpenSpec command throughout kickoff and delegated skills. Keep the selected
store sticky. Without an explicitly selected store, commands act on the nearest local
`openspec/` root.

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

## When to Use & Triggers

Use for a new idea entering the complete Software Fabric SDLC. Do not use to implement or archive an existing change.

## Workflows & Steps

1. Initialize and validate OpenSpec context.
2. Coordinate proposal, design, specs, and tasks through the responsible personas.
3. Obtain approval before handing off to implementation.

## Scripts & Tools

- Use OpenSpec initialization, context, proposal, design, and status commands.
- Use repository instructions to identify persona handoffs and required gates.

## Rules & Guidelines

- Keep planning separate from implementation and require explicit approval before apply.
- Identify testing, security, legal, review, deployment, and operations stages.

## Error Handling

| Error | Cause | Fix |
|---|---|---|
| CLI unavailable | OpenSpec is not installed or initialized | Report setup requirements and stop |
| Planning incomplete | Required artifact or approval is missing | Keep the change in planning |
| High-risk change | A legal trigger is present | Route to `stage:legal` before review or deployment |

## Scenarios & References

- Use the idea-capture, persona, security, testing, legal, operations, and SDLC specs.
- Preserve traceable handoffs through change artifacts and stage labels.

## Quick Reference

| Task | Output |
|---|---|
| Start | New OpenSpec change and proposal |
| Plan | Design, specs, and tasks |
| Handoff | Approval status and next skill, with no implementation yet |

## Collaboration & Iteration Loop

- Confirm planning decisions with the user and pass each stage through its responsible persona.

## Output Specs, Success, Evaluation & Security

- Output change name, artifacts, approval status, gates, and next skill.
- Success requires complete planning, explicit risk routing, and no premature implementation.