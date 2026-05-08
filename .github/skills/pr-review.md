# Skill: PR Code Review

**Persona:** Code Reviewer Agent  
**Input:** PR diff, design.md, coding standards  
**Output:** GitHub PR review (APPROVE / REQUEST_CHANGES) with inline comments

---

## When to Use This Skill

Use when a PR is labelled `stage:review` (security passed) and awaits code review.

---

## Execution Steps

1. **Read context** — Open `design.md` and `proposal.md` for the change
2. **Review diff** — Examine each changed file systematically
3. **Apply checklist** — Work through the review checklist below
4. **Write comments** — Inline comments with BLOCKING / SUGGESTION / QUESTION prefix
5. **Summary comment** — Overall review summary with findings count
6. **Submit review** — APPROVE or REQUEST_CHANGES on GitHub
7. **On approval** — Label PR `stage:deploy`

---

## Review Checklist

### Correctness
- [ ] All spec scenarios implemented (check against proposal.md)
- [ ] All tasks in tasks.md are checked off
- [ ] Logic handles edge cases from spec (empty inputs, large inputs, concurrent access)
- [ ] No known race conditions or TOCTOU issues

### AI-Generated Code Checks
- [ ] Auth check not silently removed — every protected path still enforces auth
- [ ] Auth logic is server-side — no permission check lives only in the client
- [ ] No inverted auth conditions (e.g. `if (!isAuthenticated) { grantAccess() }`)
- [ ] Error handling present for all failure paths — AI often generates happy-path-only code
- [ ] Null/empty-input guards present where expected
- [ ] SCA/license findings from Security Agent reviewed and resolved

### Code Quality  
- [ ] Functions ≤ 30 lines (flag longer ones with refactor suggestion)
- [ ] Cyclomatic complexity ≤ 10 per function
- [ ] No duplicate code blocks (DRY principle)
- [ ] Consistent naming with rest of codebase
- [ ] No magic numbers or strings (use named constants)

### Error Handling
- [ ] All external calls handle failures (HTTP errors, DB errors, timeouts)
- [ ] Errors propagate correctly to callers
- [ ] User-facing error messages are friendly (no stack traces, no internal IDs)
- [ ] Appropriate error logging with context (traceId, userId, etc.)

### Observability
- [ ] Structured log entries for key operations
- [ ] Metrics instrumented for new endpoints/operations
- [ ] OpenTelemetry spans added for multi-step operations

### Documentation
- [ ] Public API functions/classes have docstrings
- [ ] Complex algorithms have inline comments explaining WHY
- [ ] Breaking changes documented in a migration note

---

## Comment Format

```
🚫 BLOCKING: [specific issue]
[Code snippet showing the problem]
[Suggested fix with code]
Reference: design.md §Error Handling

💡 SUGGESTION: [improvement idea]
[What to do and why it's better]

❓ QUESTION: [clarification needed]
[What is unclear and why it matters]
```

---

## Quality Checks

- [ ] Every inline comment has a BLOCKING/SUGGESTION/QUESTION prefix
- [ ] Every BLOCKING comment has a specific suggested fix
- [ ] Design.md requirements are all verified
- [ ] Summary comment lists: total comments, blocking count, approval decision
- [ ] No vague comments ("this is bad", "refactor this")
- [ ] Review submitted within one agent session

---

## Example Summary Comment

```markdown
## Code Review Summary — add-csv-export

**Reviewer:** Code Reviewer Agent  
**Result:** 🔄 REQUEST_CHANGES (2 blocking, 3 suggestions)

### Blocking Issues
1. `src/services/export.py:45` — No error handling when DB query returns None
2. `src/api/routes.py:23` — Missing rate limit check before calling ExportService

### Suggestions
1. `src/services/export.py:12-38` — Method exceeds 30 lines; consider extracting CSV builder
2. `src/models/export.py:8` — Magic number `10` should be `MAX_EXPORTS_PER_HOUR = 10`
3. `tests/test_export.py:67` — Test name doesn't describe expected outcome

Please address blocking issues and re-request review.
```
