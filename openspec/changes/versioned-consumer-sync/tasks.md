# Tasks: Versioned Consumer Sync

## Contract and documentation

- [x] 1. Add the consumer manifest schema and ownership rules to the shared documentation.
- [x] 2. Document reserved `local/` extension paths and the shared contribution flow.

## Validation

- [x] 3. Implement a dependency-light manifest validator with explicit errors for malformed, unsupported, and unsafe values.
- [x] 4. Add deterministic validator tests for valid manifests, unsupported modes, unsafe paths, duplicate protected paths, and missing source metadata.

## Synchronization

- [x] 5. Add a reusable consumer sync workflow that validates the manifest and opens or updates a pull request without pushing to the default branch.
- [x] 6. Add conflict detection for managed paths and ensure protected local paths are excluded from updates.
- [x] 7. Add release notes and migration guidance for the first consumer adoption.

## Quality gates

- [x] 8. Run focused validation and all repository checks available in CI.
- [x] 9. Run security scanning against the new workflow and validator changes.
