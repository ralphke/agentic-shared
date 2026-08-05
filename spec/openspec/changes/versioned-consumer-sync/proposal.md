# Proposal: Versioned Consumer Sync

**Change Slug:** `versioned-consumer-sync`
**Author:** Systems Architect
**Date:** 2026-08-05
**Status:** Draft
**Priority:** P1

## Intent

Consumer repositories need a reliable way to consume shared agentic assets while preserving repository-specific agents, skills, prompts, and specifications. The current documentation describes synchronization but does not define a machine-readable contract or conflict policy.

## Scope

- [ ] Define a consumer manifest with source version, asset groups, ownership modes, and protected paths.
- [ ] Add validation for manifest shape, supported asset groups, ownership modes, and path safety.
- [ ] Add a reusable sync workflow that validates a consumer manifest and opens a reviewable pull request for updates.
- [ ] Document the contribution and conflict-resolution model for shared and consumer-specific assets.
- [ ] Add deterministic tests for valid manifests and invalid/conflicting configurations.

## Out of Scope

- Automatically merging synchronization pull requests.
- Rewriting consumer-owned files.
- Implementing a full three-way content merge engine in this change.
- Publishing private or consumer-specific repository content from the shared repository.

## Approach

Use a checked-in `.agentic-shared.yml` manifest in each consumer repository. The manifest declares the shared repository and release version, selected asset groups, ownership modes, and protected local paths. A validator runs before synchronization. A reusable workflow creates a branch and pull request, allowing normal consumer CI and human review to resolve changes.

The initial implementation establishes the contract and safe failure behavior. Content transfer remains explicit and reviewable; files outside declared managed paths are never modified by the sync workflow.

## Scenarios

### Scenario: Valid consumer manifest passes validation
- GIVEN a consumer manifest references a supported release and supported asset groups
- WHEN the manifest validator runs
- THEN validation succeeds with no warnings or errors

### Scenario: Unsupported ownership mode is rejected
- GIVEN a consumer manifest uses an ownership mode other than `managed`, `extended`, or `local`
- WHEN the manifest validator runs
- THEN validation fails with the asset group and supported modes in the error

### Scenario: Local paths are protected
- GIVEN a manifest declares a local path under `.github/skills/local/`
- WHEN synchronization is prepared
- THEN the workflow excludes that path from shared updates
- AND the workflow does not delete or overwrite the local path

### Scenario: Sync changes arrive as a pull request
- GIVEN a consumer repository has a valid manifest and a newer shared release is available
- WHEN the scheduled sync workflow runs
- THEN it creates or updates a pull request containing only declared shared asset changes
- AND the pull request includes the source version and validation result

### Scenario: Sync stops on a managed conflict
- GIVEN a consumer has modified a file declared `managed`
- WHEN synchronization detects that local content differs from the previously installed shared version
- THEN synchronization fails without overwriting the file
- AND the pull request reports the conflicting path and required resolution

## Acceptance Criteria

- [ ] A documented `.agentic-shared.yml` schema exists for consumer repositories.
- [ ] The validator accepts valid manifests and rejects unsafe or unsupported values.
- [ ] Consumer-local extension paths are explicitly protected.
- [ ] Synchronization is delivered through a pull request and never direct-pushes to the default branch.
- [ ] Managed conflicts fail closed and identify the affected paths.
- [ ] Validation tests pass in CI.

## Affected Domains

- `sdlc-process`
- `personas`
- `security-standards`
