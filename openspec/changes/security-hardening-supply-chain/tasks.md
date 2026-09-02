# Tasks: Security Hardening & Supply Chain Protection

**Change Slug:** `security-hardening-supply-chain`  
**Status:** Implemented  
**Date:** 2026-05-15

---

## Phase 1 — Critical: Make Security Gate Blocking (P0)

- [x] **T01** — Remove `continue-on-error: true` from Python SAST (bandit) step in
  `sdlc-orchestrator.yml`. Enforce `bandit -r src/ -ll` with non-zero exit on findings.
- [x] **T02** — Remove `continue-on-error: true` from pip-audit step. Add `--fail-on-vuln`
  flag so any CVE causes a non-zero exit.
- [x] **T03** — Remove `continue-on-error: true` from npm audit step. Keep
  `--audit-level high` filter.
- [x] **T04** — Add `fetch-depth: 0` to checkout in security gate (required for secrets
  history scan with gitleaks).
- [x] **T05** — Add lockfile hash pinning verification step to security gate
  (Python: check `--hash=` in requirements.txt, fail if missing in production manifests).
- [x] **T06** — Add phantom package detection step for PyPI (verify each package name
  returns HTTP 200 from pypi.org/pypi/<pkg>/json).
- [x] **T07** — Add phantom package detection step for npm (verify each package name
  returns HTTP 200 from registry.npmjs.org/<pkg>).
- [x] **T08** — Add gitleaks step scanning full branch history (`--log-opts origin/main..HEAD`).
  Use pinned image `zricethezav/gitleaks:v8.18.4`.
- [x] **T09** — Update PR comment step to reflect pass/fail status. Post a blocked
  message when `${{ job.status }}` is not `success`.

## Phase 2 — High: Supply Chain Verification Workflow (P1)

- [x] **T10** — Create `.github/workflows/supply-chain-verification.yml` triggered on
  every PR and push to main, plus weekly schedule.
- [x] **T11** — Add SBOM generation job using `anchore/syft:v1.4.1` (pinned), output
  CycloneDX JSON. Upload as PR artifact with 90-day retention.
- [x] **T12** — Add Grype vulnerability scan job against the generated SBOM.
  `--fail-on high` blocks the job on HIGH+ findings.
- [x] **T13** — Convert Grype results to SARIF and upload to GitHub Code Scanning
  (conditional on code scanning being enabled).
- [x] **T14** — Add dependency confusion detection job: verify each PyPI package against
  pypi.org; verify each npm package against registry.npmjs.org. Block on 404.
- [x] **T15** — Add lockfile integrity job: fail production `requirements*.txt` files
  that lack `--hash=` pinning. Verify `package-lock.json` is committed. Warn on missing
  .NET `packages.lock.json`.
- [x] **T16** — Add container image digest pinning job: check Dockerfiles and
  devcontainer.json for tag-only image references. Warn (not block) initially.
- [x] **T17** — Add supply chain summary job that aggregates pass/fail for all
  sub-jobs into the GitHub step summary.

## Phase 3 — Security Engineer Instructions (P1)

- [x] **T18** — Expand Core Responsibilities section:
  - Responsibility 4: Dependency Confusion Detection (new)
  - Responsibility 5: Supply Chain Verification (new, promotes lockfile + SBOM)
  - Responsibility 6: SBOM Generation (new)
  - Renumber downstream responsibilities.
- [x] **T19** — Expand Behaviour Rules:
  - Add rule: block merge if production requirements lack hash pinning.
  - Add rule: block merge on dependency confusion (public package shadows private name).
  - Add rule: block merge if secrets found anywhere in branch history (not just diff).
- [x] **T20** — Add "Supply Chain & Artifact Integrity Checks" subsection to checklist
  covering: hash pinning, transitive dep scan, dependency confusion, SBOM, image digest
  pinning, image signing, SLSA attestation, gitleaks history scan.
- [x] **T21** — Expand SAST Tools section: add gitleaks, trufflehog, syft, and grype
  commands. Add "Phantom Package Registry Verification" sub-section with curl snippets.
- [x] **T22** — Update Security Report Format: add "Supply Chain Verification" table
  to the report template. Add grype and gitleaks to the SAST Results table.

## Phase 4 — Future Work (P2, tracked as backlog)

- [ ] **T23** — Pin devcontainer base image to digest:
  `mcr.microsoft.com/devcontainers/base:ubuntu-24.04@sha256:<digest>`
  (Update `.devcontainer/devcontainer.json`; re-verify after each Microsoft image update.)
- [ ] **T24** — Add Cosign keyless image signing in `publish-devcontainer.yml` after
  the image build step. Verify signature in deployment pipeline before pull.
- [ ] **T25** — Add SLSA provenance attestation using `github-actions/attest-build-provenance`
  for built container images. Target: SLSA level 2.
- [ ] **T26** — Enable `RestoreLockedMode` in all .NET project files and commit
  `packages.lock.json` for each project. Update CI to fail if lock diverges.
- [ ] **T27** — Add `pip-compile --generate-hashes` to the developer workflow (pre-commit
  hook or CI check) so new Python dependencies are always hash-pinned at introduction.
- [ ] **T28** — Enable GitHub Branch Protection rules:
  - Require status checks: `supply-chain-verification / sbom-and-vuln-scan`,
    `supply-chain-verification / dependency-confusion`,
    `supply-chain-verification / lockfile-integrity`
  - Require PR (no direct push to main)
  - Require 1 review approval
- [ ] **T29** — Promote container image digest pinning warning to error after all base
  images in Dockerfiles and devcontainer.json have been pinned (T23 prerequisite).
- [ ] **T30** — Add `trufflehog` step as second secret scanner (defence-in-depth) once
  gitleaks has been validated in production for one sprint.

---

## Verification Checklist

Before closing this change:

- [x] `sdlc-orchestrator.yml` — security gate has no `continue-on-error: true`
- [x] `sdlc-orchestrator.yml` — gitleaks scans full branch history
- [x] `sdlc-orchestrator.yml` — phantom package check for PyPI and npm
- [x] `supply-chain-verification.yml` — SBOM generated and uploaded as artifact
- [x] `supply-chain-verification.yml` — Grype blocks on HIGH/CRITICAL
- [x] `supply-chain-verification.yml` — dependency confusion detection job present
- [x] `supply-chain-verification.yml` — lockfile integrity job present
- [x] `supply-chain-verification.yml` — container image pinning check present
- [x] `security-engineer.md` — supply chain checklist added
- [x] `security-engineer.md` — SBOM, gitleaks, grype, phantom check in SAST tools section
- [x] `security-engineer.md` — updated security report format
- [ ] T23–T30 tracked as backlog issues for Phase 4
