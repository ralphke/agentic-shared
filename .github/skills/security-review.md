# Skill: Security Review

**Persona:** Security Engineer Agent  
**Input:** PR diff, dependency manifest, codebase  
**Output:** Security report comment on PR; block or pass gate

---

## When to Use This Skill

Use when a PR is labelled `stage:security` by the QA Engineer Agent.

---

## Execution Steps

1. **Run SAST** — Execute static analysis tools for the relevant languages
2. **Scan dependencies** — Run dependency vulnerability scanner on manifest changes
3. **Phantom package check** — For every new dependency, verify it exists on the
   official registry (npm/PyPI/NuGet) and is actively maintained. AI tools occasionally
   hallucinate package names that attackers can later register (supply-chain risk).
4. **License / SCA scan** — Run a Software Composition Analysis tool; flag any
   GPL/copyleft or unknown-license package in a proprietary codebase.
5. **Check for secrets** — Review diff for any hardcoded credentials or API keys
6. **OWASP Top 10 review** — Manual checklist review of code changes
7. **AI-specific checks** — Verify auth is server-side, not inverted, and not
   client-side-only; check for missing RLS on new data surfaces; verify no
   prompt-injection risk from untrusted input passed to AI APIs
8. **Assess findings** — Classify each finding by severity (CRITICAL/HIGH/MEDIUM/LOW)
9. **Write security report** — Post structured report as PR comment
10. **Gate decision:**
    - CRITICAL or HIGH → label `security:blocked`, block merge, open remediation issues
    - MEDIUM → warning comment + backlog issue, do NOT block
    - LOW/INFO → informational only
11. **On clean/accepted** — Label `security:passed` + `stage:review`

---

## SAST Commands by Language

```bash
# Python
bandit -r src/ -ll -f json -o bandit-report.json
pip-audit --format json > pip-audit-report.json

# .NET (requires GitHub Advanced Security or dotnet-security-scan)
dotnet tool run security-scan --project src/ --format sarif

# JavaScript / TypeScript
npm audit --audit-level high --json > npm-audit.json
npx eslint . --plugin security --format json > eslint-security.json

# License / SCA scan (all languages)
# Python
pip-licenses --format=json > pip-licenses.json
# Node
npx license-checker --json > license-report.json

# Universal secret scan
# (GitHub Secret Scanning runs automatically on push)
# Additional local scan:
# gitleaks detect --source .
```

---

## OWASP Top 10 Quick Reference

| ID  | Category               | Key Questions                                         |
|-----|------------------------|-------------------------------------------------------|
| A01 | Broken Access Control  | Are all endpoints behind auth? IDOR possible?         |
| A02 | Cryptographic Failures | Any plain-text secrets? Weak hashing (MD5/SHA1)?     |
| A03 | Injection              | User input in SQL/HTML/shell/path without validation? |
| A04 | Insecure Design        | Threat model reviewed? Defense in depth applied?     |
| A05 | Misconfiguration       | Debug mode? Default credentials? Unnecessary features?|
| A06 | Vulnerable Components  | All new dependencies CVE-free?                        |
| A07 | Auth Failures          | Brute force protection? Session management secure?   |
| A08 | Software Integrity     | Supply chain verified? Build pipeline secured?        |
| A09 | Logging Failures       | Security events logged? No PII in logs?               |
| A10 | SSRF                   | Any external URL parameters? Allowlist enforced?     |

---

## Security Report Template

Post as a PR comment:

```markdown
## 🔒 Security Review — <change-slug>
**Agent:** Security Engineer  
**Date:** YYYY-MM-DD  
**Result:** ✅ PASSED / ❌ BLOCKED (N HIGH, M CRITICAL findings)

### SAST Results
| Tool     | Critical | High | Medium | Low | Info |
|----------|----------|------|--------|-----|------|
| bandit   | 0        | 0    | 1      | 2   | 0    |
| pip-audit| 0        | 0    | 0      | 0   | 0    |

### Dependency Scan
No vulnerable dependencies detected.

### OWASP Top 10 Review
- ✅ A01 Access Control — new endpoint requires valid JWT
- ✅ A03 Injection — parameterized queries used throughout
- ⚠️ A09 Logging — export audit log includes email (PII) — MEDIUM

### Findings
| ID | Severity | File | Line | Description | Recommended Fix |
|----|----------|------|------|-------------|-----------------|

### Decision
[PASSED: No blocking findings. Approved for code review.]
[BLOCKED: N HIGH findings must be resolved before review.]
```

---

## Quality Checks

- [ ] All SAST tools executed (relevant to repo languages)
- [ ] Dependency manifest changes scanned
- [ ] Phantom package check performed — all new dependencies verified on official registry
- [ ] License/SCA scan completed — no unresolved GPL/copyleft findings
- [ ] All 10 OWASP categories assessed
- [ ] AI-specific checks completed (server-side auth, no inverted logic, RLS, prompt injection)
- [ ] Security report posted on PR
- [ ] Correct gate decision made (CRITICAL/HIGH block; MEDIUM warn)
- [ ] Remediation issues opened for all blocking findings
