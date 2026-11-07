# Tasks: Separate Software Fabric from OpenSpec

## 1. Baseline and compatibility

- [x] 1.1 [S] Record a representative baseline for affected skills and
      instructions using the agreed clarity, structure, execution-guidance,
      and handoff rubric; verify each sample has a recorded score.
- [x] 1.2 [M] Declare OpenSpec 1.16.0 and Fabric's Node.js 26+ baseline in
      integration configuration; verify supported and unsupported version
      checks report their actual outcomes.
- [x] 1.3 [M] Pin the compatibility CI installation to 1.16.0 and test
      upstream CLI discovery, status, and instructions in an isolated project;
      verify the supported-version integration suite passes.

## 2. Skill and policy ownership

- [x] 2.1 [M] Separate proposal and planning orchestration into `fabric-*`
      entry points; test Fabric-default and explicit-standalone routing.
- [x] 2.2 [M] Separate apply and verification orchestration while retaining
      planning acceptance and quality gates; test missing acceptance and
      standalone invocation behavior.
- [x] 2.3 [M] Separate sync, single archive, and bulk archive orchestration;
      test blocked gates, complete delta verification, and selected stores.
- [x] 2.4 [M] Reconcile other Fabric entry points, personas, and broad
      instructions with explicit work-mode selection; test that standalone
      selection does not bypass repository controls.
- [x] 2.5 [M] Remove Fabric ownership of regenerated upstream skill bodies and
      retire or revise policy restoration and its tests; verify upstream
      refresh leaves Fabric entry points intact.
- [x] 2.6 [S] Document Fabric versus OpenSpec behavior and chat versus CLI
      invocation; verify planning, approval, sync, and archive guidance names
      the correct owner and direct-CLI limitations.

## 3. Revision-bound gate evidence

- [x] 3.1 [M] Define the versioned evidence-manifest schema and lifecycle
      applicability rules; test valid, missing, duplicate, malformed, and
      unsupported-schema entries.
- [x] 3.2 [M] Implement trusted-source and revision validation for evidence;
      test untrusted claims, stale heads, unavailable sources, and
      scope-backed non-applicability; validate different-revision mapping
      identity, authorized producer, freshness, and externally verified links.
- [x] 3.3 [M] Collect configured exact GitHub check and review evidence for
      pre-merge gates; test accepted, failed, missing, and superseded results
      without treating a generic approval as a different gate.
- [x] 3.4 [M] Add the stable required merge check using protected evaluator and
      configuration inputs; test current-head binding and exclusion of the
      check's own result.
- [x] 3.5 [M] Evaluate applicable release evidence against the release
      revision; test missing and failing release gates block progression.
- [x] 3.6 [M] Integrate post-deployment and archive evidence into Fabric
      preflight; test missing operational evidence prevents spec writes and
      archive moves; test valid different-revision mapping, invalid or
      superseded release/deployment links, and preserved same-SHA behavior.
- [x] 3.7 [M] Security-review the evaluator's trust boundary and workflow
      permissions; test that untrusted PR code and author-supplied passing
      claims cannot satisfy required controls.
- [x] 3.8 [S] Document evidence sources, required branch-protection setup,
      failure modes, and direct CLI limitations; verify each documented
      required check corresponds to an actual check.

## 4. Consumer migration

- [x] 4.1 [M] Add sync preflight for formerly shared `openspec-*` paths;
      test that customized, consumer-owned, and protected paths are never
      silently overwritten or deleted.
- [x] 4.2 [M] Implement reviewed migration of unchanged formerly shared skills
      only when upstream replacements and Fabric entry points are available;
      test successful migration and missing-replacement failure.
- [x] 4.3 [S] Verify the recommended manifest retains local product specs and
      protected active changes; test local-root default and explicit
      shared-store selection.
- [x] 4.4 [S] Document entry-point migration, supported versions, upstream
      update review, and rollback; verify the instructions preserve consumer
      local extensions and OpenSpec stores.

## 5. Integrated validation and handoff

- [x] 5.1 [M] Run integrated scenario tests for Fabric and standalone modes,
      ownership, consumer sync, all three evidence lifecycle points, and
      unsupported OpenSpec versions, including trusted different-revision
      mapping and its failure cases; record exact commands and results.
- [x] 5.2 [S] Reassess the baseline samples using the same rubric and record
      the before/after scores and differences.
- [x] 5.3 [S] Record the security review, applicable legal-risk assessment,
      and remaining administrator actions; verify missing evidence is
      reported without claiming merge, release, or archive clearance.

## Workflow follow-up

- Obtain required review and all applicable quality-gate evidence before
  archive; configure required checks in the target repository separately.
