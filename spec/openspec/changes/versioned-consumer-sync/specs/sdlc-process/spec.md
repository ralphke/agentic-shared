# Delta for sdlc-process

## ADDED Requirements

### Requirement: Versioned Consumer Asset Contract

The shared asset repository MUST publish a versioned, machine-readable contract that consumer repositories can use to select shared asset groups and declare ownership modes.

#### Scenario: Consumer selects shared asset groups
- GIVEN a consumer repository has a `.agentic-shared.yml` manifest
- WHEN the manifest is validated
- THEN it identifies a source repository and release version
- AND each selected asset group uses a supported ownership mode

### Requirement: Reviewable Consumer Synchronization

Consumer synchronization MUST be delivered as a pull request and MUST NOT overwrite the consumer default branch directly.

#### Scenario: Synchronization opens a pull request
- GIVEN a valid consumer manifest references a newer shared release
- WHEN the sync workflow runs
- THEN it creates or updates a pull request containing the declared shared asset changes
- AND the pull request identifies the source release and validation result

### Requirement: Consumer Ownership Protection

Synchronization MUST preserve consumer-owned paths and MUST fail closed when a managed shared path has unreviewed local modifications.

#### Scenario: Managed conflict blocks synchronization
- GIVEN a managed shared file differs from the consumer's previously installed version
- WHEN synchronization evaluates the update
- THEN the file is not overwritten
- AND the workflow reports the conflicting path for human resolution

#### Scenario: Local extension remains unchanged
- GIVEN a consumer file exists beneath a declared protected local path
- WHEN synchronization runs
- THEN the file remains unchanged regardless of the shared release contents
