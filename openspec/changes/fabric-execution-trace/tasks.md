# Tasks

Implement only the repo-local pilot described in [design.md](./design.md).
Requirements and scenarios are in
[the capability delta](./specs/fabric-execution-tracing/spec.md). Leave managed
assets and existing uncommitted customizations unchanged.

## 1. Trace identity and durable storage

- [x] 1.1 Add `scripts/fabric_trace.py` using the Python standard library with
      versioned trace/event validation, an explicit resolved change directory,
      repository identity, immutable target revision, UUIDs, and predecessor
      links. Verify with focused `unittest` cases for both planning trees,
      duplicate slugs, unsupported versions, mismatched repositories/revisions,
      and missing paths.
- [x] 1.2 Implement locked event appends and atomic report/metadata writes,
      validating path containment and reporting truncated events, stale locks,
      and conflicting writers explicitly. Verify persistence across separate CLI
      processes plus malformed-stream, concurrency, and unsafe-path tests.
- [x] 1.3 Add the exact `.fabric-traces/` ignore entry and start
      `doc/fabric-execution-trace.md` with initialization/resume examples,
      schema fields, storage boundaries, and the workstation trust limitation.
      Verify `git check-ignore` for generated files and execute the documented
      initialization against a temporary Git repository.

## 2. Activity recording and observed command execution

- [x] 2.1 Implement `record` with distinct instruction-discovery/inclusion,
      skill-load, agent-invocation, and stage-claim kinds; manual records cannot
      select trusted provenance or gate status. Verify that fabricated all-stage
      success and unverified session references remain self-reported.
- [x] 2.2 Implement `run` with argument-array execution, start/completion
      pairing, UTC timestamps, exit-code propagation, dirty-workspace detection,
      and interruption diagnostics. Verify success, nonzero exit, process-launch
      failure, missing completion, and workspace/revision changes using harmless
      child processes in temporary repositories.
- [x] 2.3 Add allowlisted metadata handling, credential-shaped value
      rejection/redaction, safe URL handling, and Markdown escaping; omit raw
      arguments, prompts, environments, and stdout/stderr from stored records.
      Verify sentinel-secret absence in events, evidence, and reports, while
      child output remains available to the caller.
- [x] 2.4 Document `record` and `run` examples, the difference between observed
      execution and validation success, and data-sharing precautions. Verify
      every example with the focused CLI tests and confirm no secret-bearing
      test data is a real credential.

## 3. Stage contracts and readiness evaluation

- [x] 3.1 Define and validate the versioned policy and typed evidence formats
      for all nine stages described in the design, including trusted producers,
      planning artifact hashes, coverage, required scanners, legal assessments,
      review approvals, deployment lineage, and operations observations. Verify
      malformed evidence rejection and include a documented conservative example
      policy that leaves unconfigured producers missing.
- [x] 3.2 Implement gate evaluation and legal not-applicable rules with separate
      activity status, actionable missing-evidence reasons, and the specified
      gate states. Verify labels, checked tasks, green jobs without structured
      results, coverage below 80 percent, omitted scanners, HIGH/CRITICAL
      findings, and unapproved high-risk legal cases never satisfy gates.
- [x] 3.3 Implement revision invalidation, effective rerun/approval selection,
      predecessor history, and prerequisite ordering. Verify stale approvals,
      edits after validation, unrelated successful reruns, deploy-before-review,
      and mismatched deployed artifacts cannot yield verified-complete; valid
      reruns retain prior failures.
- [x] 3.4 Document each stage contract, outcome semantics, and the difference
      between all stages observed and verified-complete. Verify a
      requirement-to-test mapping covers every delta-spec scenario.

## 4. Read-only GitHub evidence collection

- [x] 4.1 Implement `collect-github` with `gh api` argument arrays and
      pagination for PR head metadata, run attempts, jobs/steps, effective
      approvals, artifact metadata, and deployment/status references. Verify
      mocked responses for pagination, duplicate names, retries, fork repository
      mismatches, skipped/cancelled steps, stale SHAs, and dismissed/blocking
      reviews.
- [x] 4.2 Retrieve only policy-selected bounded evidence artifacts, reject
      unsafe archive paths or oversized inputs, and validate provenance against
      the matching producer/run/attempt. Verify arbitrary local JSON cannot
      become provider-verified evidence and test expired, missing, malformed,
      and wrong-attempt artifacts.
- [x] 4.3 Verify Git/tree or artifact lineage when merge/deployment identifiers
      differ from the reviewed source revision. Test a valid lineage and an
      unrelated successful deployment; require the latter to remain unverified.
- [x] 4.4 Persist collection errors and return nonzero for authentication,
      authorization, network, or schema failures without promoting cached
      evidence. Verify mocked failures and assert the collector invokes no
      GitHub mutation, workflow dispatch, merge, or deployment operation.
- [x] 4.5 Document read-only permissions, evidence producer configuration,
      source links, refresh behavior, and the current orchestrator's
      label-trigger and warning-only test limitations. Verify guide commands
      against mocked CLI interactions without requiring network credentials.

## 5. Unified reports and local skill integration

- [x] 5.1 Implement `report` and `check` using one evaluated result for JSON and
      Markdown, with every stage, timeline, provenance, evidence IDs/URLs,
      policy digest, target revision, observation boundary, and next actions.
      Verify output consistency, incomplete-check nonzero exit, rendering of
      partial traces, and explicit invalid-input errors.
- [x] 5.2 Add `.github/skills/local/fabric-trace/SKILL.md` with discoverable
      tracing trigger phrases, an explicit apply-skill invocation, traced
      validation commands, optional read-only PR collection, and honest final
      reporting. Verify its frontmatter and references, exercise the documented
      flow, and confirm generic apply skills/prompts and managed
      instructions/workflows are unchanged.
- [x] 5.3 Add deterministic positive lifecycle and negative evidence fixtures
      plus focused integration tests, with a sticky simulation marker in both
      report formats. Verify synthetic completeness, missing deploy/operate,
      high-risk legal blocking, forged activity, changed policy/revision, and
      online-unavailable revalidation produce the required results.
- [x] 5.4 Complete the guide with Windows PowerShell examples, expected report
      output, ordinary-apply limitations, manual host-debug inspection,
      simulation disclosure, and targeted rollback/retention instructions.
      Execute the examples against temporary repositories and ensure no example
      implies automatic persona dispatch or real deployment from fixtures.

## 6. Cross-surface validation and real partial pilot

- [x] 6.1 Run `python -m unittest discover -s tests -p "test_fabric_trace*.py"`
      and the repository's applicable existing validation. Verify the full
      scenario mapping passes and record exact commands/results without
      installing additional dependencies unless required.
- [x] 6.2 Run a real trace against an available committed revision using local
      execution evidence and any authorized read-only GitHub evidence. Verify
      missing providers and dirty-workspace activity remain visible and that
      absent deploy/operate evidence prevents verified-complete; do not create a
      commit, mutate GitHub, or deploy solely to make the pilot green.
- [x] 6.3 Run the complete synthetic lifecycle separately, verify the visible
      simulation marker and all nine stage rows in both formats, and compare
      with the real partial pilot. Review the final diff to confirm only the
      approved local implementation surfaces changed and pre-existing
      customizations were preserved.

## Workflow follow-up

- Review this proposal and evidence contracts before starting implementation.
- Request reusable upstream integration separately after the local pilot; do not
  edit managed assets in place.
- Archive only after applicable project quality gates pass. A successful tooling
  demonstration is not evidence that an actual application's full Fabric
  lifecycle ran.
