# Tasks

## 1. Define the Layered Contract

- [ ] 1.1 Update the canonical `Proposal Structure` requirement in
      `openspec/specs/idea-capture/spec.md` from the accepted delta, preserving
      all retained scenarios, and verify strict OpenSpec validation reports no
      warning for that requirement.
- [ ] 1.2 Add canonical requirements for proposal format precedence, capability
      traceability, and bounded legacy compatibility from the delta, and verify
      each requirement has at least one strict-valid scenario.
- [ ] 1.3 Update `openspec/templates/idea-to-spec.md` to describe composition from
      CLI-provided core instructions plus Software Fabric extensions without
      copying the package template, and verify every required extension appears
      once.

## 2. Align Proposal Entry Points

- [ ] 2.1 Update the Product Owner agent's proposal creation and format rules to
      use CLI artifact instructions as the schema core and the local contract as
      its extension, and verify the legacy primary headings are no longer
      generated or presented as canonical.
- [ ] 2.2 Update `idea-to-spec` and `openspec-propose` skill guidance so both
      obtain the core template through OpenSpec instructions, apply identical
      extension requirements, and stop on unreconcilable conflicts; verify their
      wording and required-section lists remain aligned.
- [ ] 2.3 Update directly related cross-references and examples that teach the
      proposal shape, including Product Owner examples and OpenSpec workflow
      guidance, and verify repository search finds no contradictory canonical
      section list.

## 3. Add Proposal Composition Validation

- [ ] 3.1 Extend `.github/scripts/validate_openspec_change.py` with focused
      proposal checks for schema core sections, required Software Fabric
      extensions, scenario and acceptance counts, capability declaration
      parsing, and exact delta-path correspondence; verify each check fails
      explicitly with an actionable message.
- [ ] 3.2 Add bounded legacy aliases for `Intent` and `Affected Domains` without
      weakening extension, capability, scenario, UX, or acceptance checks, and
      verify malformed or contradictory mixed headings fail.
- [ ] 3.3 Add focused unit tests for a valid layered proposal, missing core and
      extension sections, missing or duplicate capability mappings, unrelated
      deltas, valid legacy compatibility, invalid mixed aliases, and new
      generation not requiring legacy headings; verify the validator test module
      passes.

## 4. Verify Planning Contract Consistency

- [ ] 4.1 Add or update regression checks that compare the canonical requirement,
      template, Product Owner persona, and proposal command skills for mandatory
      extension and precedence terms, and verify the focused policy tests pass.
- [ ] 4.2 Run `openspec validate "unify-openspec-proposal-format" --strict --json`
      and verify the change has no errors or warnings.
- [ ] 4.3 Run the focused OpenSpec and proposal-validator tests plus the
      repository's applicable test command, and record exact commands and
      results without claiming external security, review, CI, or archive gates.
- [ ] 4.4 Review `git diff` for scope and migration consistency, confirming no
      archived proposal was reformatted and no runtime, dependency, API,
      database, or infrastructure file changed; report any unrelated dirty
      worktree files separately.

## Workflow follow-up

- Obtain security, code-review, CI, coverage, and other required gate evidence
  before archive.
- Sync and verify the `idea-capture` delta against its canonical source spec.
- Archive the change only after all mandatory gates are evidenced; then verify
  the archived proposal, delta synchronization, and removal of active-change
  blockers.
