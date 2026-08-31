# Proposal: Migrate Prompt Entry Points to OpenSpec Skills

**Change Slug:** `migrate-prompts-to-openspec-skills`
**Author:** Product Owner Agent
**Date:** 2026-08-31
**Status:** Approved
**Priority:** P1

---

## Intent

OpenSpec's current distribution is skills-first. This repository still publishes four
Copilot prompt files as its SDLC entry points, which creates a compatibility gap as
prompt-file support is retired and upstream OpenSpec evolves its command skills.

Replace the shared prompt entry points with compatible skill definitions that preserve
the Software Fabric controls while using OpenSpec's artifact-driven CLI workflow.

## Scope

- Map `.github/prompts/opsx-propose.prompt.md` to a proposal-creation skill.
- Map `.github/prompts/opsx-apply.prompt.md` to an implementation skill.
- Map `.github/prompts/opsx-verify.prompt.md` to a verification skill.
- Map `.github/prompts/sdlc-kickoff.prompt.md` to an explicitly scoped orchestration skill,
  or retire it when the upstream skills make the wrapper redundant.
- Use `SKILL.md` front matter and command naming compatible with current OpenSpec skills.
- Establish OpenSpec CLI installation and initialization as a prerequisite for shared command
  skills that invoke `openspec`.
- Preserve Software Fabric legal, security, testing, and stage-gate requirements.
- Update the shared manifest, sync behavior, documentation, and tests for the new asset model.
- Define a migration period before removal of the existing prompt paths.

## Out of Scope

- Changing the Software Fabric personas, quality thresholds, or legal-review policy.
- Modifying consumer repositories directly.
- Replacing OpenSpec's CLI or forking its schema implementation.
- Migrating consumer-specific assets under `.github/prompts/local/` without consumer approval.

## Approach

Use OpenSpec v1.11.0 distributed skills as the behavioral baseline: `openspec-propose`,
`openspec-apply-change`, and `openspec-verify-change`. Add shared skills that invoke the
OpenSpec CLI for artifact discovery and instructions, then layer only this repository's
persona and quality-gate rules. Maintain compatibility aliases or documentation during a
defined transition period, remove prompt assets only after sync tests prove consumer
manifests handle the asset-group change safely.

The command skills require Node.js 26 or later and the OpenSpec CLI installed with
`npm install -g @fission-ai/openspec@latest`. Consumer setup guidance must run
`openspec init` while preserving this repository's `spec/openspec/` layout and verify the
result. If the CLI is absent, a command skill must stop before changing planning or code
artifacts and report the prerequisite and installation command; it must not silently fall
back to the retired prompt workflow.

## Build/Buy/Vibe

**Buy/adopt:** consume upstream OpenSpec's maintained skill conventions and CLI behavior.
**Build:** retain only the thin Software Fabric policy layer needed by this shared repository.

## Legal/IP Notes

No PII, regulated data, proprietary algorithm, or third-party content is introduced.
Upstream OpenSpec is MIT-licensed; implementation must preserve applicable attribution and
license notices if upstream text is copied rather than independently adapted.

## Scenarios

### Scenario: Create a complete change plan through the proposal skill
- GIVEN a user supplies a new feature or fix request
- WHEN the proposal skill is invoked
- THEN it creates every OpenSpec artifact required before implementation using CLI-provided
  instructions and paths
- AND it stops before modifying implementation code

### Scenario: Implement an existing OpenSpec change through the apply skill
- GIVEN a selected change has required planning artifacts and pending tasks
- WHEN the apply skill is invoked
- THEN it reads the CLI-provided context files and implements only pending tasks
- AND it records completed tasks only after the requested behavior is implemented

### Scenario: Verify a change through the verification skill
- GIVEN a selected change has implementation evidence
- WHEN the verification skill is invoked
- THEN it reports completeness, correctness, and coherence against the change artifacts
- AND it enforces this repository's test, security, legal, and review gates before archive

### Scenario: Preserve consumers during the prompt retirement transition
- GIVEN a consumer manifest requests shared SDLC assets
- WHEN the shared release is synchronized
- THEN the consumer receives the replacement skills and updated documentation
- AND the synchronization reports a clear migration action instead of silently deleting
  locally extended prompt assets

### Scenario: Prepare a consumer for command skills
- GIVEN a consumer adopts a release containing the replacement command skills
- WHEN the consumer follows the shared setup documentation
- THEN it installs Node.js 26 or later and `@fission-ai/openspec`
- AND it runs `openspec init` with the shared `spec/openspec/` layout retained
- AND a verification command confirms the CLI can resolve the consumer's OpenSpec root

### Scenario: Stop safely when the OpenSpec CLI is unavailable
- GIVEN a user invokes a replacement command skill in a repository without `openspec`
- WHEN the skill checks its prerequisites
- THEN it reports that the OpenSpec CLI is required and provides the installation command
- AND it does not create, modify, or archive OpenSpec artifacts
- AND it does not invoke the legacy prompt implementation as a fallback

### Scenario: Reject ambiguous legacy command selection
- GIVEN a user invokes a legacy prompt alias without a uniquely identifiable target change
- WHEN more than one active change is available
- THEN the skill asks the user to select a change
- AND it does not modify a change folder or implementation code

## Acceptance Criteria

- [x] Each of the four shared prompt responsibilities is mapped to a retained, replaced, or
  explicitly retired skill with documented rationale.
- [x] Replacement skills use `SKILL.md` front matter and are compatible with the current
  OpenSpec distributed skill conventions.
- [x] The proposal skill preserves a planning-only boundary and creates the full transitive
  set of artifacts required by the selected OpenSpec schema.
- [x] The apply and verify skills obtain change state and context through the OpenSpec CLI
  rather than assuming fixed artifact paths.
- [x] Documentation states the command-skill prerequisites: Node.js 26 or later,
  `npm install -g @fission-ai/openspec@latest`, and repository initialization with
  `openspec init` while retaining `spec/openspec/` paths.
- [x] Documentation includes an executable verification step that confirms `openspec` can
  resolve the repository's OpenSpec root after initialization.
- [x] Command skills stop without modifying artifacts when the OpenSpec CLI is unavailable,
  clearly report the prerequisite, and do not fall back to legacy prompts.
- [x] Software Fabric testing, security, legal-review, and approval gates remain enforced.
- [x] Sync tests cover managed, extended, and local consumer assets during the transition.
- [x] README and consumer migration guidance document the replacement command names and
  retirement schedule.
- [x] GitHub issues labelled `idea` are the primary non-developer proposal intake, while
  direct `/opsx:propose` remains a supported issue-free alternative.

## Affected Domains

- `sdlc-process`
- `personas`