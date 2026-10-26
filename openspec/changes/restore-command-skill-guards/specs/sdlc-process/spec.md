# Delta for sdlc-process

## ADDED Requirements

### Requirement: Repository Command Contracts Survive CLI Updates

Post-update automation MUST restore repository-owned command-skill contracts
and wrapper deprecations without replacing surrounding generated content.
Maintainers MUST invoke restoration, review diffs, and pass script tests before
releasing shared assets, without weakening assertions.

#### Scenario: Regeneration removes a required guard

- GIVEN an OpenSpec CLI update regenerates shared skills or legacy prompt wrappers
- WHEN a maintainer invokes the documented restoration automation
- THEN it restores Node.js 26+ prerequisites, fail-closed CLI/context
  checks, no-legacy-fallback behavior, and replacement-skill notices
- AND retains the current CLI's store-selection and root-resolution behavior
- AND the maintainer reviews diffs and runs the full shared-script suite before releasing

#### Scenario: Restoration is repeatable and preserves generated content

- GIVEN all expected target files have recognized layouts
- WHEN restoration runs and is then run again
- THEN the first run changes only repository-owned policy blocks
- AND all surrounding content and newline styles are preserved
- AND the second run leaves every already-correct file byte-for-byte unchanged

### Requirement: Restoration Rejects Unsupported Inputs

Restoration MUST validate all targets before writing any. Missing files,
ambiguous insertion points, malformed markers, or conflicting policy blocks
MUST produce actionable errors and a nonzero exit with all targets unchanged.
Write-time failures MUST be reported explicitly, including any completed writes.

#### Scenario: Unsupported input prevents all restoration writes

- GIVEN any target is missing, has ambiguous anchors, or has malformed or
  conflicting policy blocks
- WHEN restoration preflights the targets
- THEN it reports the affected file and reason with a nonzero exit
- AND all target files remain byte-for-byte unchanged

### Requirement: Restored Contracts Preserve Workflow Boundaries

Restored policy blocks MUST preserve supported proposal entry paths, stage
boundaries, truthful task completion, and security and required legal gates.

#### Scenario: Restored contracts preserve stage boundaries and intake

- GIVEN regenerated command assets have been reconciled
- WHEN their contract tests run
- THEN issue-based and direct proposals remain supported
- AND proposal execution remains planning-only
- AND apply cannot mark partial or deferred work complete
- AND verification does not replace security or required legal approval

### Requirement: Pull Requests Validate Shared Script Contracts

Every pull request in the canonical `ralphke/agentic-shared` repository MUST run
the complete shared-script test suite with its dependencies installed. Consumer
copies lacking synchronized script tests MUST skip this canonical-only job.
Test failures and import errors MUST fail the job.
The job MUST run with read-only repository permissions and MUST NOT depend on
repository secrets or suppress failing tests.

#### Scenario: Pull request removes a contract

- GIVEN a canonical-repository pull request removes a required guard or wrapper notice
- WHEN the shared-script CI job runs
- THEN contract tests fail and the job reports failure
- AND CI does not run restoration on the checkout to conceal the missing contract

#### Scenario: Synchronized workflow skips consumer repositories

- GIVEN a consumer repository receives the workflow without the canonical script tests
- WHEN its pull request triggers the workflow
- THEN the canonical-only shared-script job is skipped

#### Scenario: Clean CI environment runs the full suite

- GIVEN a clean runner without preinstalled test dependencies
- WHEN the shared-script CI job runs
- THEN it installs PyYAML and discovers every `.github/scripts/test_*.py` module
- AND import failures or assertion failures produce a nonzero test exit status
