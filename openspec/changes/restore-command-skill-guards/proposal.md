# Proposal

## Why

CLI regeneration and earlier refactoring removed repository-specific command-skill
guards and prompt deprecation notices while their contract tests remained unchanged.
Restore those contracts through repeatable post-update automation, with explicit
release review and independent pull-request validation to catch future drift.

## What Changes

- Restore the Node.js 26+ prerequisite, CLI/context failure stop behavior, and
  no-legacy-fallback guard in propose, apply, and verify command skills.
- Restore issue-based and direct proposal intake documentation, planning-only
  boundaries, truthful task completion, and existing security/legal gate guidance
  wherever the current contract tests reveal missing text or behavior.
- Restore deprecation notices in the three affected legacy prompt wrappers.
- Add a post-`openspec update` restoration script (option 2(b)) that reapplies
  identifiable repository-owned policy blocks without replacing generated workflows.
- Document script invocation, generated-diff review, and script tests in the README.
- Add canonical-repository pull-request CI for the full `.github/scripts` unittest
  suite with PyYAML; skip consumers because script tests are not synchronized.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `sdlc-process`: Add durable requirements for preserving repository command-skill
  contracts during CLI regeneration and validating those contracts on pull requests.

## Impact

- Shared assets: three OpenSpec command skills and their three prompt wrappers.
- Documentation: README release/update checklist.
- Tooling: a bounded restoration script and fixture-based regression tests.
- CI: a focused shared-script test workflow and its configuration contract tests.
- Dependencies: PyYAML for test imports, installed explicitly in CI.
- Existing OpenSpec store-selection and root-resolution behavior remains intact.
- The existing migration change already specifies command prerequisites and intake
  behavior in an unsynced delta. This change restores that implementation without
  duplicating or replacing its `Idea-First Development` modification.

## Non-goals

- No automatic CLI updates, blind text replacement, or whole-file regeneration
  by the restoration script.
- No CLI downgrade, whole-file rollback, test weakening, consumer synchronization,
  branch-protection mutation, merge, deployment, spec sync, or archive.
- No changes to `fabric-execution-trace` or other existing worktree changes.

## Acceptance Criteria

1. Propose, apply, and verify retain current CLI workflows and satisfy the existing
   command-skill tests, including prerequisite and fail-closed behavior.
2. Idea issues and direct proposals remain documented entry paths, and the three
   legacy wrappers clearly name their replacement skills.
3. A post-update script restores policy blocks, preserves surrounding CLI content,
   and leaves already-correct files byte-for-byte unchanged on repeated runs.
   Missing or conflicting inputs fail preflight before any target file is written.
4. The README documents explicit script invocation after updates, diff review,
   the exact full script-test command, and dependency setup.
5. CI runs the full script suite on every pull request in `ralphke/agentic-shared`
   with read-only permissions and PyYAML available; failures fail the job.
   The job skips synchronized consumer copies that lack these script tests.
6. Focused regression tests, the full script suite, and OpenSpec change validation
   pass before implementation is marked complete.

## Legal Risk Assessment

Low risk: governance text, test configuration, and release documentation only.
No new sensitive-data handling, external data integration, or redistributed
third-party content. Reassess if implementation expands the scope.
