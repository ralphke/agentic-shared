# Design

## Context

See [proposal.md](proposal.md) for motivation and scope. Current command assets
carry `generatedBy: "1.14.3"` and contain store-aware CLI workflows. Existing
`test_openspec_command_skills.py` asserts repository-specific wording as well as
handoff and entry-path contracts. Earlier validation reported seven failures;
PyYAML installation resolved the two previous import errors.

The main `sdlc-process` spec does not yet include the command-skill migration.
The active `migrate-prompts-to-openspec-skills` delta already defines
prerequisites and intake behavior. This delta adds update reconciliation and CI
obligations without modifying that change or claiming its source-spec sync has
occurred.

## Goals / Non-Goals

**Goals:**

- Restore contracts additively while keeping current CLI behavior.
- Automate repeatable policy restoration while retaining review and independent
  regression detection.
- Preserve existing stage handoffs and all unrelated worktree changes.

**Non-Goals:**

- Replacing generated workflows, relaxing tests, or automatically running CLI
  updates.
- Operating on consumers, changing branch protection, or claiming CI was
  executed remotely when only local validation is available.

## Decisions

### ADR 1: Reconcile current generated content instead of restoring old files

Use `3f813e1~1` only as a reference for repository policy, not as a wholesale
rollback. Add prerequisite/stop sections to propose, apply, and verify; make the
planning-only boundary explicit, retain truthful completion in apply, and retain
security/legal gate constraints in verify. Keep existing store-aware commands
and root resolution. Restore replacement-skill banners in the three legacy
wrappers.

Missing CLI or incompatible Node stops before artifact changes. Context failures
report setup errors without legacy fallback, while preserving the generated
workflow's distinction between an auto-selected uninitialized project and an
explicit setup request. No implicit initialization or stale-root fallback.

Alternative rejected: rewriting tests to match upstream-generated text would
discard the repository's documented consumer policy.

### ADR 2: Bounded post-update restoration (option 2(b))

Add `.github/scripts/restore_openspec_contracts.py`, explicitly invoked after
`openspec update`; it does not invoke the CLI or rewrite generated workflows.
Keep repository-owned policy text as identifiable, delimited blocks in this
script and the six target assets. Do not duplicate the policy in separate
template files or restore historical whole files.

Use a fixed allowlist of the three command skills and three prompt wrappers.
Resolve targets relative to the script's repository root, not an arbitrary
working directory. Preflight every target before writing any: require existing,
readable files, valid expected frontmatter, unambiguous insertion anchors, and
either no owned block or exactly one complete recognized block in its expected
location. Reject missing files, duplicate anchors, malformed markers, or
conflicting blocks with actionable file-specific errors and a nonzero exit. Do
not guess an insertion location or overwrite conflicting customizations.

Compute all edits before writing. Insert owned policy blocks only at recognized
boundaries, preserving all other bytes, including frontmatter and newline style.
If a correct block already exists, leave the file byte-for-byte unchanged.
Report changed and already-correct files explicitly. Preflight failure leaves
every target unchanged; write-time errors must also be reported, identifying any
files already changed rather than claiming a multi-file atomic transaction.

The README checklist records CLI version, config backup before initialization,
the intended CLI update, explicit restoration-script invocation, diff review,
context verification, and full script tests. Include PowerShell commands with an
explicit interpreter, PyYAML setup, and
`-m unittest discover -s .github\scripts -p "test_*.py"`. Disable bytecode
writes because tracked script bytecode exists. Do not run `openspec update`
during implementation; use regenerated fixtures.

Alternative rejected: option 2(a) relies on maintainers repeatedly editing
policy text correctly. Automation reduces omissions but still needs human review
when upstream semantics change. Unsupported layouts stop for deliberate
reconciliation, not a permissive fallback.

### ADR 3: Dedicated minimal-permission script CI

Add `.github/workflows/shared-script-tests.yml` rather than coupling fast unit
tests to security scans or the manual archive gate. Trigger on every pull
request, pushes to main, and manual dispatch; do not filter paths. Use
`contents: read`, an explicit supported Python version, explicit PyYAML
installation, and the full unittest discovery command. Follow existing
action-version conventions.

As confirmed during implementation, guard the job with
`github.repository == 'ralphke/agentic-shared'`. Workflow assets are
synchronized to consumers but `.github/scripts` is not an asset group, so
consumer copies must skip this canonical-only check. Do not expand script
distribution in this change.

Test the workflow configuration structurally using the existing PyYAML
dependency, accounting for YAML boolean interpretation of the `on` key. Assert
triggers, the canonical-repository guard, least-privilege permissions,
dependency installation, complete discovery, and no failure suppression. Add
command-skill and README assertions for the newly documented update contract;
preserve existing assertions.

Test restoration in temporary repository-shaped fixtures: clean regenerated
inputs, already-correct files, repeated invocation, missing files, duplicate
anchors, malformed or conflicting owned blocks, and preserved unrelated bytes
and newline styles. Assert all targets remain byte-for-byte unchanged after any
preflight failure. CI runs these tests but must not invoke restoration on the
checkout to mask missing committed policy blocks.

CI failure supplies a check result, but enforcing required checks in branch
protection remains an administrator action outside this change.

## Risks / Trade-offs

- Script invocation can be forgotten -> explicit checklist plus independent
  pull-request contract tests that do not repair the checkout.
- Wording tests can pass despite contradictory prose -> review full edited
  sections, including missing-root and store error paths, not only string hits.
- Full-file restoration could regress CLI behavior -> additive changes and
  store/root regression assertions.
- Overlapping migration delta -> add uniquely named requirements only; leave the
  existing migration artifacts and source specs untouched.
- Future CLI layouts or semantics may change -> reject unsupported structures
  before writes, review diffs, and deliberately update fixtures and anchors.
- Partial write-time failure -> report exact progress and failure; reruns are
  idempotent, but no cross-file atomicity is claimed.

## Migration Plan

1. After planning approval, restore contracts in the six affected shared assets.
2. Add the restoration script, fixture tests, README checklist, and dedicated CI
   workflow with independent contract tests.
3. Run focused tests, full script tests, and strict OpenSpec change validation.
4. Review the diff against existing worktree state; leave trace work unchanged.
5. Submit for the normal test, security, and review gates. Reassess legal risk
   if scope expands; current governance-only changes introduce no legal-risk
   trigger.

Rollback only this change's asset, script, README, test, and workflow edits
through a reviewed reversal. Do not revert unrelated work or archive either
active change.
