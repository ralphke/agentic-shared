# Tasks

## 1. Restore Shared Command Contracts

- [x] 1.1 Restore Node.js 26+, CLI availability, context resolution, and
      no-legacy-fallback guards in propose, apply, and verify without reverting
      current store/root workflows. Restore missing planning-only,
      truthful-completion, security/legal, and issue/direct-intake wording.
      Extend command-skill assertions for retained store/root and stop behavior;
      verify
      `python -m unittest discover -s .github\scripts -p "test_openspec_command_skills.py"`
      passes.
- [x] 1.2 Restore deprecation notices naming the replacement command skills in
      `opsx-propose.prompt.md`, `opsx-apply.prompt.md`, and
      `opsx-verify.prompt.md`, retaining their current CLI workflow content.
      Verify the existing wrapper replacement tests pass and review the three
      diffs for unintended changes.

## 2. Automate Post-Update Restoration

- [x] 2.1 Implement `.github/scripts/restore_openspec_contracts.py` for the six
      fixed target assets using identifiable repository-owned policy blocks.
      Preflight all targets and compute edits before writing; reject missing
      files, invalid frontmatter, ambiguous anchors, malformed markers, and
      conflicting blocks with actionable nonzero failures and no
      preflight-failure writes. Preserve surrounding bytes and newline styles,
      report changed/already-correct files and write failures explicitly, and
      verify fixture tests cover regenerated inputs, repeat runs,
      already-correct inputs, preserved content/newlines, and unchanged bytes
      across all targets for each preflight failure. Do not invoke the CLI
      update.
- [x] 2.2 Document option 2(b) in README update policy: record CLI version,
      preserve config on initialization, explicitly invoke restoration after
      regeneration, review diffs, verify context, and run full script tests with
      explicit interpreter/dependency commands and bytecode disabled. Add
      focused documentation assertions; execute the documented restoration
      command against temporary fixtures and verify a second run makes no
      changes.
- [x] 2.3 Add `shared-script-tests.yml` for every pull request, pushes to main,
      and manual dispatch using read-only permissions, explicit Python setup,
      PyYAML installation, and full script unittest discovery. Guard the job to
      the canonical repository so synchronized consumers lacking script tests
      skip it. Add structural workflow tests covering triggers, repository
      scope, dependency setup, complete discovery, failure propagation, and
      absence of checkout-repair invocation; verify those tests pass and
      document that branch protection must be configured separately.

## 3. Integration Validation

- [x] 3.1 Run
      `.venv\Scripts\python.exe -m unittest discover -s .github\scripts -p "test_*.py"`
      with `PYTHONDONTWRITEBYTECODE=1`, resolve all failures introduced by or
      coupled to this change without weakening assertions, and verify
      `openspec validate restore-command-skill-guards --strict --json` passes.
      Review changed-file scope against the initial worktree, preserve all trace
      and unrelated changes, and report local results separately from unexecuted
      remote CI/review gates.

## Workflow follow-up

- Submit the completed change through the normal security and code-review gates.
- Do not merge, synchronize source specs, or archive without a separate request
  and verified applicable quality gates.
