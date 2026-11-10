# Tasks: orchestrate-fabric-end-to-end

Sizes: **S** means a few hours, **M** means half a day, and **L** means a full
day. Do not start a group until the previous group is verified.
Implementation requires explicit acceptance of the complete current plan and
an implementation authorization.

## 1. Execution Feasibility Gate (blocks every later group)

- [ ] 1.1 [S] Verify the exact Copilot CLI version on npm. Pin it in a
      throwaway workflow on a sandbox branch. Verify: `copilot --version`
      in the run log matches the pin.
- [ ] 1.2 [M] Inventory every persona's tools, MCP bindings, dependencies,
      permissions, and CLI or adapter ownership. Document exercised runner
      equivalents and gaps without changing responsibilities. Verify: the
      capability matrix covers the complete roster and blocks missing
      required bindings rather than assuming editor MCP portability.
- [ ] 1.3 [L] Run every CLI-dispatched persona in an authorized sandbox with
      a restricted tool set, `--no-ask-user`, and `--share`, using the maintainer's
      `COPILOT_GITHUB_TOKEN` without repository write credentials. Verify: each has a transcript proving persona
      loading, required bindings, and denied-tool refusal; adapter-owned
      personas have verified handoff contracts.
- [ ] 1.4 [S] Record the go or no-go result against ADR-2 criteria in
      `design.md`. If any check fails, stop and re-plan with `gh aw`.
      Verify: the decision row and run URL are present in `design.md`.

## 2. Coordinator Core: State, Approvals, Transitions

- [ ] 2.1 [M] Add the orchestration config schema and loader for
      `.github/fabric/orchestration.yml`, with defaults `enabled: false` and
      the documented limits. Verify: unit tests cover defaults, invalid
      values, and narrowing-only `stage_paths`.
- [ ] 2.2 [M] Implement planning-digest computation and the stage ledger
      reconstruction from OpenSpec `status --json` and GitHub evidence
      fixtures. Verify: unit tests show identical output when inputs are
      replayed or reordered.
- [ ] 2.3 [M] Implement the approval parser and validator for the `/fabric`
      commands. Bind each approval to the digest and head SHA, check actor
      permission, and distinguish explicit human approval from agent output
      without requiring a separate Copilot account.
      Permit one human's ordered planning approvals, not self-review at
      delivery. Document reduced assurance. Verify: tests cover a valid single
      planning approver using their own credential, agent approval spoofing, stale digests,
      unauthorized actors, and malformed commands.
- [ ] 2.4 [L] Implement the transition validator for the full lifecycle. This
      includes conditional UX/legal routing, missing or conflicting
      applicability blocks, and bounded retry and rework. Verify: one table
      test per lifecycle edge and per blocker code.
- [ ] 2.5 [M] Implement dispatch-key idempotency, duplicate and stale result
      rejection, and the cancellation state. Verify: tests cover duplicate,
      concurrent, out-of-order, stale-revision, and interrupted-run fixtures.
- [ ] 2.6 [S] Add spoofed-evidence tests. A stage label, an agent
      `completed` result, a checked task, or a look-alike check from an
      untrusted source must not open any boundary. Verify: tests pass in
      `shared-script-tests.yml`.
- [ ] 2.7 [M] Implement external-head detection and `/fabric adopt
      <full-head-sha>`, superseding running results and revalidating artifacts
      without preserving stale approvals. Document Chat/cloud-agent coexistence
      and recovery. Verify: fixture tests cover adoption, a racing update,
      unchanged and changed planning, and no dispatch before renewed approvals.
- [ ] 2.8 [M] Implement per-change dispatch/time reservations and dated
      owner-supplied charge estimates. Document limits versus provider billing.
      Verify: tests cover missing assumptions, concurrent reservations,
      failed/cancelled/superseded attempts, unknown durations, and retry/adoption
      without budget reset or bypass.

## 3. Persona Execution and Validated Publish

- [ ] 3.1 [M] Add a reusable persona-execution workflow. It uses
      `contents: read`, the pinned CLI, the stage prompt built from the Fabric
      skill, untrusted text in delimited data blocks, a stage tool allowlist,
      a timeout, and result, patch, and transcript artifacts. Verify: the
      workflow contract test checks permissions, the absence of gate or deploy
      secrets, pinned actions, and the artifact names.
- [ ] 3.2 [M] Extract the shared prerequisite composite action and reuse it
      from CLI execution and the cloud agent's `copilot-setup-steps` wrapper.
      Pin OpenSpec 1.16.0 and preserve the cloud job name; keep CLI installation
      separate. Document both entry points. Verify: workflow contracts and
      setup runs prove matching prerequisites, trusted-base resolution in
      privileged jobs, and no shared-setup privileged secrets.
- [ ] 3.3 [M] Implement result-schema validation and the stage path allowlist
      for the publish step. Reject traversal, symlinks, workflow, config,
      policy, and `openspec/specs/**` edits, and require a base SHA match.
      Use an expected-SHA ref update without force-pushing over external work.
      Verify: unit tests for each rejection, one accepted patch, and a head
      moving between validation and publication.
- [ ] 3.4 [M] Add the publish job. It applies the validated patch to
      `fabric/<slug>`, opens or updates a draft PR, and blocks fork PRs.
      Verify: the workflow contract test and a fixture dry run produce the
      expected commit and draft-PR intent.
- [ ] 3.5 [S] Document the persona invocation contract and result schema in
      the relevant Fabric skills and persona handoff notes. Do not change
      `openspec-*` skills. Verify: the ownership tests still pass.

## 4. Orchestrator and Task Router Integration

- [ ] 4.1 [L] Rework `sdlc-orchestrator.yml` to run the coordinator from the
      base ref on the documented events, with per-change concurrency. Keep the
      existing structural validation. Verify: the workflow contract test
      checks triggers, permissions, the absence of PR-code checkout in
      privileged jobs, and concurrency.
- [ ] 4.2 [M] Implement the status publisher. It writes the Actions summary,
      a coordinator-owned status comment, informational
      `Fabric orchestration / <stage>` checks, stage labels mirroring state,
      default `stage:proposal`, and conflict flags. Verify: tests show that
      every eligible fixture event emits route, stage, status, reference, and
      next action, plus reduced-assurance identity status, adoption blockers,
      consumed/reserved usage, and sourced cost estimates where applicable.
- [ ] 4.3 [M] Convert `copilot-task-router.yml` to intake-only Fabric routing
      with standalone reporting through `route_fabric_workflow.py`. Remove the
      direct implementation request and assignment. Verify: the contract test
      asserts that no `addAssignees` call and no implementation request text
      remain.
- [ ] 4.4 [S] Verify the disabled path. With orchestration disabled or no
      credential, report `BLOCKED:ORCHESTRATION_DISABLED` and dispatch
      nothing. Verify: fixture test and contract test.

## 5. Delivery Boundaries, Adapters, and Archive

- [ ] 5.1 [M] Add maintainer-only authorization preflight for merge-triggered
      delivery, Fabric manual starts and reruns, and reusable adapter entry
      points. Verify authenticated PR merger/base/revision and configured
      numeric actor ID; bind continuations to verified originating runs.
      Document scope and administrator limitations. Verify: fixtures cover the
      maintainer, other users, bot/auto-merges, ambiguous lookup, wrong targets,
      rerun actors and forged continuations; workflow contracts require the
      preflight before privileged work and preserve automatic PR CI.
- [ ] 5.2 [M] Route merge, release, and archive to the existing
      `fabric-*-gate` controls only. Report disabled protected operations or
      missing evidence as blocked. Verify: tests show no merge, publish,
      deploy, or archive call when `FABRIC_PROTECTED_OPERATIONS_ENABLED` is
      off.
- [ ] 5.3 [M] Implement deploy and operations adapter dispatch and evidence
      binding to the merged SHA. A missing adapter yields
      `BLOCKED:ADAPTER_MISSING`. Verify: fixture tests cover configured,
      failed, and missing adapters.
- [ ] 5.4 [S] Require `fabric-verify-change`, complete delta verification, and
      fresh archive-gate evidence before sync or move. Verify: tests cover a
      stale archive evidence fixture and an unverified delta fixture.

## 6. Documentation, Sync, and Administration

- [ ] 6.1 [M] Document prerequisites, permissions, credential separation,
      single-maintainer credential reuse, consumer-specific delivery actor IDs,
      configuration, cost limits, commands, and rollback in the README and
      `fabric-workflow.instructions.md`. Verify: the documented commands match
      the parser tests.
- [ ] 6.2 [S] Add `.github/fabric/**` to the protected local paths and add the
      example config to the shared sync manifest. Verify: the manifest
      validator and sync tests pass. Consumer-local stores are untouched.

## 7. Security and Legal-Risk Review

- [ ] 7.1 [M] Security review of the new workflows and coordinator. Cover
      prompt injection, token scope, `pull_request_target` and `workflow_run`
      misuse, publish validation, and action pinning. Run actionlint and
      zizmor (#21) on the new files. Verify: there are no unresolved HIGH or
      CRITICAL findings.
- [ ] 7.2 [S] Legal-risk assessment for sending repository content to Copilot
      under the owner's existing terms. Confirm that no new provider is added.
      Escalate to `stage:legal` if a trigger applies. Verify: the result is
      recorded on the PR.

## 8. Isolated Demonstration and Handoff

- [ ] 8.1 [L] With separate explicit authorization, run an isolated end-to-end
      demonstration on a demo change. Record the actual persona executions
      with references, plus a negative path such as missing implementation
      authorization. Label fixture/dry-run results separately. Verify: the
      demonstration record states that it does not grant production clearance.
- [ ] 8.2 [S] Run the full shared script tests, `openspec validate --strict`,
      and `git diff --check`. Hand off to review with the coverage evidence.
      Verify: all checks pass, and coverage of the new modules is at least
      80%.

## Workflow follow-up

- After review, merge, and the required gates, archive with
  `/fabric-archive-change orchestrate-fabric-end-to-end`. This requires fresh
  archive evidence and complete delta verification.
- Enabling orchestration and protected operations in any repository is a
  separate, explicitly authorized administrative action (#22).
