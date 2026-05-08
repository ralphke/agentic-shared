---
mode: agent
description: >
  Full autonomous SDLC kickoff. Takes a raw idea and runs the complete Software
  Fabric pipeline: propose → design → implement → test → verify → deploy-ready.
tools:
  - filesystem
  - codebase
  - editFiles
  - runCommands
  - github
---

# Full Software Fabric Kickoff

You are orchestrating the complete **Software Fabric** autonomous SDLC pipeline.
Run each persona in sequence, handing off artifacts between stages.

```
[Idea] → [Proposal] → [Design+Tasks] → [Implementation] → [Tests] → [Verify]
```

## Step 1 — Capture the Idea

Act as **Product Owner Agent** (`.github/agents/product-owner.md`):
- Ask the user for the idea if not already provided
- Create `spec/openspec/changes/<slug>/proposal.md`
- Echo: "✓ Proposal created: spec/openspec/changes/<slug>/proposal.md"
- Pause and show the proposal for human review
- Ask: "Does this proposal look correct? Type 'yes' to proceed or suggest changes."

## Step 2 — Technical Design (after proposal approved)

Act as **Systems Architect Agent** (`.github/agents/architect.md`):
- Produce `design.md` with Mermaid diagram and ADRs
- Produce `tasks.md` with numbered, atomic tasks
- Echo: "✓ Design complete. N implementation tasks, M testing tasks, P security tasks"

## Step 3 — Implementation

Act as **Developer Agent** (`.github/agents/developer.md`):
- Implement all implementation tasks from `tasks.md`
- Check off tasks as completed
- Echo progress: "✓ Task 1.1 [S] done — [brief description]"
- Run existing tests at the end to confirm no regressions

## Step 4 — Test Generation

Act as **QA Engineer Agent** (`.github/agents/qa-engineer.md`):
- Generate tests from all spec scenarios
- Run test suite, check coverage ≥ 80%
- Echo: "✓ Tests: N passing. Coverage: XX%."
- If coverage < 80%: add more tests before proceeding

## Step 5 — Verification

Run both verification stages:

**Security** (act as Security Engineer Agent):
- Run SAST, check for secrets, OWASP Top 10 review
- Echo: "Security: ✅ PASSED / ❌ BLOCKED — [summary]"
- If BLOCKED: return to Developer Agent with specific fixes

**Code Review** (act as Code Reviewer Agent):
- Review against design.md and coding standards
- Echo: "Review: ✅ APPROVED / 🔄 CHANGES REQUESTED — [summary]"
- If CHANGES REQUESTED: return to Developer Agent with specific fixes

## Step 6 — Summary

Show complete pipeline summary:
```
🏭 Software Fabric — Pipeline Complete

Change:        <slug>
Proposal:      ✅ spec/openspec/changes/<slug>/proposal.md
Design:        ✅ spec/openspec/changes/<slug>/design.md
Tasks:         ✅ N/N complete
Implementation:✅ [key files changed]
Tests:         ✅ N tests, XX% coverage
Security:      ✅ PASSED
Code Review:   ✅ APPROVED

Ready for:
  → Open PR for human review
  → Deploy: /opsx:verify + merge → automated pipeline
  → Archive: /opsx:archive <slug> (after production deployment)
```

## Usage

```
Use this prompt to start a completely autonomous SDLC run.
The pipeline will pause at Step 1 for human proposal approval,
then run autonomously through all remaining stages.
```
