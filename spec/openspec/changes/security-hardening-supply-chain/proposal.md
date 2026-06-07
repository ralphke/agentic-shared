# Proposal: Security Hardening & Supply Chain Protection

**Change Slug:** `security-hardening-supply-chain`  
**Author:** Security Engineer Agent  
**Date:** 2026-05-15  
**Status:** Accepted  
**Priority:** P0 — Critical

---

## Problem Statement

The Software Fabric SDLC has well-written security engineer instructions and a security
gate in the pipeline, but several critical gaps allow vulnerabilities and supply chain
attacks to pass undetected:

1. **Security checks were non-blocking** — all steps used `continue-on-error: true`,
   meaning findings were logged but never blocked a merge.
2. **No supply chain attack detection** — dependency confusion, phantom/hallucinated
   packages, and lockfile tampering were not automatically detected in CI/CD.
3. **No SBOM generation** — there was no Software Bill of Materials, making it
   impossible to audit what packages shipped, respond to incidents, or verify provenance.
4. **Missing secrets history scan** — secret scanning only covered the current diff,
   not the full branch history.
5. **Container images not digest-pinned** — tag-only references allow silent base image
   substitution between builds.

---

## Goals

1. Make every security check blocking on HIGH/CRITICAL findings.
2. Automatically detect supply chain attacks: phantom packages, dependency confusion,
   lockfile tampering.
3. Generate a CycloneDX SBOM on every PR for auditability.
4. Scan full git branch history for secrets (not just the current diff).
5. Warn when container base images lack digest pinning.
6. Expand security engineer instructions to include all new controls.

---

## Out of Scope

- Container image signing with Cosign (separate change)
- SLSA provenance attestation level 2+ (separate change)
- Runtime security monitoring (separate change)
- Penetration testing automation (separate change)

---

## Acceptance Criteria

- [ ] `sdlc-orchestrator.yml` security gate fails the build on any HIGH/CRITICAL SAST or
  dependency finding.
- [ ] `sdlc-orchestrator.yml` phantom package check runs on every `stage:security` PR and
  blocks merge if any dependency is not found on PyPI or npm.
- [ ] `supply-chain-verification.yml` workflow runs on every PR and generates a
  CycloneDX SBOM, uploads it as a build artifact, and runs Grype vulnerability scan.
- [ ] `supply-chain-verification.yml` detects and blocks dependency confusion attacks
  by verifying each package name against the official registry.
- [ ] `supply-chain-verification.yml` verifies lockfile integrity (hash pinning).
- [ ] `supply-chain-verification.yml` warns on container images that lack digest pinning.
- [ ] `security-engineer.md` instructions include supply chain section with SBOM,
  dependency confusion, and lockfile requirements.
- [ ] `security-engineer.md` checklist includes enforceability items for all new controls.
- [ ] `security-engineer.md` SAST tools section includes gitleaks full-history scanning
  and phantom package verification commands.
- [ ] Security report format includes a Supply Chain Verification section.

---

## Risk & Rollback

**Risk:** Blocking security gates may surface existing issues in the repo, causing
CI failures on open PRs. Mitigation: run the new workflow on `workflow_dispatch` first
to assess the baseline before enabling on all PRs.

**Rollback:** Revert the three changed files:
- `.github/workflows/sdlc-orchestrator.yml`
- `.github/agents/security-engineer.md`
- `.github/workflows/supply-chain-verification.yml` (delete)
