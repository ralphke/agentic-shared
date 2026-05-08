---
mode: agent
description: >
  Verify a Software Fabric change — run security review and code review to
  validate implementation against the spec and quality gates.
tools:
  - filesystem
  - codebase
  - runCommands
  - github
---

# `/opsx:verify` — Verify a Change

Run the verification pipeline: Security → Code Review → Gate Check.

## Stage 1: Security Review

Act as **Security Engineer Agent** (`.github/agents/security-engineer.md`).
Apply skill: `.github/skills/security-review.md`

1. Run SAST tools for the project's languages:
   ```bash
   # Python
   python3 -m bandit -r src/ -ll 2>/dev/null || true
   # .NET
   # dotnet security-scan (if installed)
   ```
2. Check for hardcoded secrets in changed files
3. Review OWASP Top 10 checklist for changed code
4. Produce security report:
   - CRITICAL/HIGH findings → BLOCKED (list findings with fixes)
   - MEDIUM findings → WARNING (list findings, do not block)
   - Clean → PASSED

## Stage 2: Code Review

Act as **Code Reviewer Agent** (`.github/agents/code-reviewer.md`).
Apply skill: `.github/skills/pr-review.md`

1. Read `design.md` and `proposal.md` for the change
2. Review all changed files against the review checklist
3. Produce review summary:
   - BLOCKING issues → REQUEST_CHANGES (list with suggested fixes)
   - SUGGESTIONS → informational
   - Clean → APPROVE

## Stage 3: Gate Check

Verify all quality gates from `spec/openspec/config.yaml`:
- [ ] Tests passing (`python3 -m pytest` or `dotnet test`)
- [ ] Coverage ≥ 80% (from QA stage)
- [ ] Security scan: no CRITICAL/HIGH
- [ ] Code review: no BLOCKING issues
- [ ] All tasks in `tasks.md` checked off
- [ ] All acceptance criteria in `proposal.md` checked off

## Usage

```
/opsx:verify add-csv-export
/opsx:verify     ← verify the most recent in-flight change
```

## Output

```
Security Review: ✅ PASSED (0 critical, 0 high, 1 medium warning)
Code Review:     ✅ APPROVED (2 suggestions, 0 blocking)
Gate Check:
  ✅ Tests: 42 passing
  ✅ Coverage: 84%
  ✅ Security: clean
  ✅ Review: approved
  ✅ Tasks: 8/8 complete
  ✅ Acceptance Criteria: 5/5 checked

Ready to archive: /opsx:archive add-csv-export
```
