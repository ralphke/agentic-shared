---
mode: agent
description: >
  Implement a Software Fabric change end-to-end through the persona pipeline:
  Architect (design+tasks) → Developer (code) → QA (tests). 
  Runs autonomously through all implementation stages.
tools:
  - filesystem
  - codebase
  - editFiles
  - runCommands
  - github
---

# `/opsx:apply` — Implement a Change

Work through the full implementation pipeline for a change.
Check which stage the change is currently in and continue from there.

## Stage Detection

1. Check `spec/openspec/changes/<slug>/` for existing artifacts
2. If only `proposal.md` → start with Architect (design + tasks)
3. If `design.md` exists but no code → start with Developer
4. If code exists but no tests → start with QA Engineer
5. If tests exist → run QA coverage check, then proceed to security prompt

## Stage 1: Architect (if `design.md` missing)

Act as **Systems Architect Agent** (`.github/agents/architect.md`).
Apply skill: `.github/skills/spec-to-design.md`

- Read `proposal.md` and existing codebase structure
- Produce `design.md` with component diagram, ADRs, API contracts
- Produce `tasks.md` with numbered, atomic, estimated tasks
- Echo: "✓ Design complete. N tasks created."

## Stage 2: Developer (if implementation tasks unchecked)

Act as **Developer Agent** (`.github/agents/developer.md`).

- Read `design.md` and `tasks.md`
- Implement each unchecked implementation task in order
- Check off each task as it is completed
- Echo: "✓ Task 1.1 [S] done" for each completed task
- Run existing tests to confirm nothing is broken

## Stage 3: QA Engineer (if testing tasks unchecked)

Act as **QA Engineer Agent** (`.github/agents/qa-engineer.md`).
Apply skill: `.github/skills/test-generation.md`

- Read all spec scenarios from `specs/<domain>/spec.md`
- Generate tests: ≥ 1 per scenario, covering all acceptance criteria
- Run test suite and check coverage ≥ 80%
- Echo: "✓ Tests: N passing. Coverage: XX%."

## Usage

```
/opsx:apply add-csv-export         ← apply a specific change
/opsx:apply                        ← apply the most recent in-flight change
```

## Completion Output

```
✓ Design: spec/openspec/changes/<slug>/design.md
✓ Tasks: spec/openspec/changes/<slug>/tasks.md (N tasks)
✓ Implementation: N tasks completed
✓ Tests: N tests, XX% coverage
  
Ready for: Security review → run /opsx:verify <slug>
           Or create a PR for manual review
```
