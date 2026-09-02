---
agent: agent
description: >
  Full autonomous SDLC kickoff. Takes a raw idea and runs the complete Software
  Fabric pipeline: propose → design → implement → test → verify → deploy-ready.
tools: [execute/getTerminalOutput, execute/sendToTerminal, execute/runInTerminal, read, edit/editFiles, search/codebase, 'github/*']
---

> **Deprecated:** This wrapper is retained for one compatibility release. Use the
> `software-fabric-kickoff` skill for new workflows; it requires Node.js 26+ and the OpenSpec CLI.
> Until that release, this prompt continues to run the pipeline below as-is.

# Full Software Fabric Kickoff

You are orchestrating the complete **Software Fabric** autonomous SDLC pipeline.
Run each persona in sequence, handing off artifacts between stages.

Before Step 1, verify Node.js 26+ and the OpenSpec CLI are installed. If either is
missing, tell the user to install them (or use the `software-fabric-kickoff` skill
instead) and stop.

```
[Idea] → [Proposal] → [Design+Tasks] → [Implementation] → [Tests] → [Verify]
```

## Step 1 — Capture the Idea

Act as **Product Owner Agent** (`.github/agents/product-owner.agent.md`):
- Ask the user for the idea if not already provided
- Create `openspec/changes/<slug>/proposal.md`
- Include Build/Buy/Vibe and Legal/IP Notes sections when applicable
- Echo: "✓ Proposal created: openspec/changes/<slug>/proposal.md"
- Pause and show the proposal for human review
- Ask: "Does this proposal look correct? Type 'yes' to proceed or suggest changes."
- If the user does not respond, or explicitly declines without suggesting changes,
  stop the pipeline and do not proceed to Step 2.

## Step 2 — Technical Design (after proposal approved)

Act as **Systems Architect Agent** (`.github/agents/architect.agent.md`):
- Produce `design.md` with Mermaid diagram and ADRs
- Produce delta specs in `specs/<domain>/spec.md` using the OpenSpec delta format
- Produce `tasks.md` with numbered, atomic tasks
- If files for this slug already exist, ask the user whether to overwrite, merge, or
  resume from the existing artifacts.
- Echo: "✓ Design complete. N implementation tasks, M testing tasks, P security tasks"

## Step 3 — Implementation

Act as **Developer Agent** (`.github/agents/developer.agent.md`):
- Implement all implementation tasks from `tasks.md`
- If a task cannot be completed due to ambiguity or missing information, pause and
  ask the user for clarification before proceeding to remaining tasks
- If the user does not respond to the clarification request, stop the pipeline and
  escalate as in Step 1.
- Check off tasks as completed
- Echo progress: "✓ Task 1.1 [S] done — [brief description]"
- Run existing tests at the end to confirm no regressions
- If existing tests fail due to the new changes, fix the regression before proceeding
  to Step 4. If failures are unrelated to this change, note them in the summary and
  continue.

## Step 4 — Test Generation

Act as **QA Engineer Agent** (`.github/agents/qa-engineer.agent.md`):
- Generate tests from all spec scenarios
- Run test suite, check line coverage ≥ 80% using the project's configured coverage
  tool (e.g., pytest-cov, jest --coverage)
- Echo: "✓ Tests: N passing. Coverage: XX%."
- If coverage < 80%: add more tests before proceeding

## Step 5 — Verification

Run the two verification stages in order. Run Code Review only after Security passes.

**Security** (act as Security Engineer Agent):
- Run SAST, check for secrets, OWASP Top 10 review
- Echo: "Security: ✅ PASSED / ❌ BLOCKED — [summary]"
- If BLOCKED: halt immediately without running Code Review, return to Step 3
  (Developer Agent) with specific fixes, then re-run Steps 4 and 5 in full

**Code Review** (act as Code Reviewer Agent, run only after Security passes):
- Review against design.md and coding standards
- Echo: "Review: ✅ APPROVED / 🔄 CHANGES REQUESTED — [summary]"
- If CHANGES REQUESTED: return to Step 3 (Developer Agent) with specific fixes,
  then re-run Steps 4 and 5 in full

Track failures separately per stage. If Security fails 3 times in a row, or Code
Review fails 3 times in a row, stop the autonomous pipeline and escalate to the user
with a summary of unresolved issues.

## Step 6 — Summary

Show complete pipeline summary:
```
🏭 Software Fabric — Pipeline Complete

Change:        <slug>
Proposal:      ✅ openspec/changes/<slug>/proposal.md
Design:        ✅ openspec/changes/<slug>/design.md
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
The pipeline will pause at Step 1 for human proposal approval, then run
autonomously through all remaining stages, looping back to Step 3 only when
Security or Code Review blocks the change (capped at 3 retry cycles per stage
before escalating to the user).
```
