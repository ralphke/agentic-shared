# Security Standards — Source of Truth

> **Domain:** `security-standards` | **Owner:** security-engineer  
> Defines security requirements, OWASP alignment, threat modelling standards,
> and the security gate process for all Software Fabric changes.

---

## Overview

Security is a first-class citizen in the Software Fabric. Every change MUST
pass a security review before it can progress to code review or deployment.
This spec defines the minimum security bar and the automated scanning process.

---

## Requirements

### Requirement: OWASP Top 10 Compliance
All application code MUST be reviewed against the OWASP Top 10 vulnerability categories.

**OWASP Top 10 Checks (enforced per change):**
1. A01 — Broken Access Control: verify AuthN/AuthZ on every new endpoint
2. A02 — Cryptographic Failures: no plain-text secrets, use TLS everywhere
3. A03 — Injection: parameterized queries, input validation, output encoding
4. A04 — Insecure Design: threat model reviewed for new components
5. A05 — Security Misconfiguration: no debug endpoints, secure defaults
6. A06 — Vulnerable Components: no known CVEs in new dependencies
7. A07 — Auth Failures: no hard-coded credentials, MFA where applicable
8. A08 — Software Integrity: signed commits, verified build pipeline
9. A09 — Logging Failures: security events MUST be logged (auth, access, errors)
10. A10 — SSRF: validate all outbound URL inputs

#### Scenario: New endpoint passes access control check
- GIVEN a new API endpoint that requires authentication
- WHEN the Security Agent reviews it
- THEN the endpoint is confirmed to require a valid token/session
- AND unauthorized requests return HTTP 401 (not 403 or 200)

#### Scenario: Hard-coded secret is detected and blocked
- GIVEN a PR introducing `API_KEY = "sk-abc123"` in source code
- WHEN the secret scanner runs
- THEN the PR is blocked with label `security:secrets-detected`
- AND the file path and line number are reported
- AND the developer is instructed to use environment variables or Key Vault

---

### Requirement: Static Analysis (SAST)
All code changes MUST pass automated static analysis before code review.

**Required SAST tooling:**
- Python: `bandit` (security linting) + `safety` (dependency CVE scan)
- .NET: `dotnet security-scan` or GitHub Advanced Security CodeQL
- JavaScript/TypeScript: `eslint-plugin-security` + `npm audit`
- All languages: GitHub Secret Scanning enabled on the repository

**Severity thresholds:**
| Severity  | Action                           |
|-----------|----------------------------------|
| CRITICAL  | Block merge, open P0 issue       |
| HIGH      | Block merge, open P1 issue       |
| MEDIUM    | Warning comment, track in backlog|
| LOW/INFO  | Informational comment only       |

#### Scenario: SAST finds SQL injection risk
- GIVEN a Python function that interpolates user input into a SQL string
- WHEN `bandit` runs SAST on the code
- THEN a HIGH severity finding is reported
- AND the PR merge is blocked until the finding is remediated

#### Scenario: SAST produces clean report
- GIVEN a PR with no static analysis findings
- WHEN SAST completes
- THEN a summary comment confirms "✅ SAST: No findings"
- AND the PR is labelled `security:sast-passed`

---

### Requirement: Dependency Vulnerability Scanning
All dependency changes (new packages, version bumps) MUST be scanned for CVEs.

**Process:**
1. Generate SBOM (Software Bill of Materials) on every PR
2. Cross-reference SBOM against OSV (Open Source Vulnerabilities) database
3. Block merge on HIGH+ CVEs in direct dependencies
4. Report MEDIUM CVEs in transitive dependencies as warnings

#### Scenario: New dependency with known CVE is blocked
- GIVEN a PR adding `some-library==1.2.3` with a known CVE-2024-XXXXX (HIGH)
- WHEN the dependency scan runs
- THEN the PR is blocked with the CVE details, CVSS score, and available fix version
- AND an issue is opened to track upgrading to a patched version

---

### Requirement: Secret Management
Secrets MUST NOT appear in source code, commit history, or log output.

**Mandated practices:**
- Use environment variables or a secrets manager (Azure Key Vault, GitHub Secrets)
- Enable GitHub Secret Scanning on the repository
- Enable GitHub Push Protection to block commits containing secrets
- Rotate all secrets exposed in commit history immediately

#### Scenario: Secret scanning prevents push
- GIVEN a developer attempts to push a commit containing an API key
- WHEN GitHub Push Protection evaluates the commit
- THEN the push is rejected before reaching the remote
- AND the developer receives instructions to remove the secret and use env vars

---

### Requirement: Security Review Sign-off
Every change MUST have a security review sign-off before deployment.

**Sign-off criteria:**
- Security scan report reviewed by Security Engineer Agent
- All CRITICAL and HIGH findings resolved or formally accepted with justification
- Security summary comment added to PR referencing the findings report
- PR labelled `security:passed` before Code Reviewer stage begins

#### Scenario: Accepted risk with justification
- GIVEN a MEDIUM finding that is a false positive for the specific use case
- WHEN the Security Engineer Agent formally accepts the risk
- THEN a comment documents: finding ID, reason for acceptance, reviewer, date
- AND the finding is logged in a security exceptions register

---

### Requirement: Secure Deployment Defaults
All deployments MUST use security hardened defaults.

**Deployment security checklist:**
- [ ] No debug endpoints exposed in production
- [ ] HTTPS enforced for all external endpoints
- [ ] Security headers set (HSTS, CSP, X-Frame-Options, etc.)
- [ ] Principle of least privilege for service identities
- [ ] Network policies restrict pod-to-pod communication (if Kubernetes)
- [ ] Secrets injected at runtime (not baked into images)
- [ ] Container images scanned for CVEs before deployment
