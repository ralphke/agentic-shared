# Tasks

Implementation remains blocked until the current proposal/spec and design are
accepted. Sizes: S = hours; M = half day. Dependencies are explicit below.
All checkboxes describe implementation work, not planning completion.

## 1. Conditional Persona and Skill Contracts

- [x] 1.1 [M] Update Product Owner, UX Designer, Architect, Developer, and QA
  personas for visual-only UX inputs and direct nonvisual handoffs. Extend
  `tests/test_ux_designer_stage.py` for both routes and run that focused pytest
  file; verify no persona requires a nonvisual UX brief.
- [x] 1.2 [M] After 1.1, align idea-to-spec, UX design, spec-to-design,
  test-generation, kickoff, and directly affected OpenSpec planning skills and
  shared instructions. Document applicability and the two routes in README;
  extend and run the relevant skill/handoff contracts and lint changed guidance.

## 2. Shared Applicability and Evidence Gate Helper

- [x] 2.1 [M] Implement proposal applicability and visual-brief validation in
  `.github/skills/test-generation/scripts/validate_ux_gate.py`. Add focused
  unittest fixtures in `.github/scripts/test_validate_ux_gate.py` for valid
  visual/CLI/API scope, invalid or duplicate decisions, escaping paths, missing
  briefs, and explicit read errors. Verify the real CLI succeeds for nonvisual
  fixtures containing no UX files and document its invocation in the QA skill.
- [x] 2.2 [M] After 2.1, add visual criterion/report validation and configured
  check-result evaluation. Document the report schema and `UX_CHECK_NAMES`;
  extend fixtures for missing/duplicate/unknown criteria, absent evidence,
  failed or blocked results, stale check revisions, pending or failed checks,
  and successful current-head checks. Run the helper unittest file and verify
  nonvisual execution needs no UX configuration or check lookup.

## 3. Orchestrator Integration

- [x] 3.1 [M] After 1.2 and 2.1, integrate per-change applicability into the
  orchestrator's UX, design, and test-entry gates and stage comments. Recheck
  active gates on PR head updates and handle archived paths explicitly. Add
  workflow integration fixtures for visual, CLI/API, mixed, and multi-change
  routing; run them alongside the focused persona contracts and document
  migration for existing proposals.
- [x] 3.2 [M] After 2.2 and 3.1, require visual validation evidence and named
  current-head consumer UX checks before test completion/security entry,
  preserving normal functional test execution. Use bounded waiting with
  explicit timeout/error reporting and least-needed check-read permissions.
  Add integration cases for pending/failed/missing checks, missing evidence,
  and the nonvisual no-lookup route; run them and document consumer CI setup
  and protected-workflow adoption.

## 4. Reconciled and Canonical Specifications

- [x] 4.1 [M] After 1.2, reconcile the overlapping UX deltas in
  `add-ux-designer-persona` and `strengthen-ux-designer-brief-workflow` with the
  conditional contract. Record supersession in their planning context without
  deleting work or claiming renewed implementation approval. Verify no delta
  can restore mandatory nonvisual UX, preserve unrelated requirements, and
  strictly validate both affected changes.
- [x] 4.2 [M] After 4.1, use `openspec-sync-specs` to merge the relevant UX
  deltas and this change's three domain deltas. Update directly related
  canonical overview text, persona counts, inputs, diagrams, and collaboration
  guidance. Extend the existing contracts to verify canonical requirements
  rather than only active deltas; run them, compare merged scenarios, and
  validate resulting specs. Do not sync unrelated changes or archive anything.

## 5. Cross-Contract Verification

- [x] 5.1 [S] After 3.2 and 4.2, run the focused UX pytest file, helper unittest
  file, and directly affected existing shared workflow/skill test suites.
  Verify both real CLI nonvisual fixtures require no UX artifacts or tooling
  and visual failures remain blocked. Record the before/after guidance
  assessment using the existing assessment format, distinguishing contract
  evidence from real consumer UX validation.
- [x] 5.2 [S] After 5.1, lint all changed Markdown, run `git diff --check`, and
  strictly validate this change and both reconciled UX changes. Review the
  final diff for unrelated edits, report any unverified external gates, and
  leave archive, release, and commit actions unperformed unless requested.
