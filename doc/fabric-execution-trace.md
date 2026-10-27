# Fabric execution trace pilot

The trace CLI is an opt-in local pilot for recording activity and collecting
revision-bound evidence for one OpenSpec change. It does not run the Software
Fabric stages automatically, and it does not turn a stage claim into verified
gate evidence.

## Initialize a trace

Start from a committed repository revision. Give `--change-dir` the explicit
path to the change directory; a change slug is not accepted because a repository
may contain more than one OpenSpec planning tree.

```powershell
$traceDir = (python scripts/fabric_trace.py init `
  --repo . `
  --change-dir openspec/changes/fabric-execution-trace).Trim()
if ($LASTEXITCODE -ne 0) { throw "Trace initialization failed." }
```

`$traceDir` contains the printed path under `.fabric-traces/<traceId>/`; keep it
for later commands in this PowerShell session. Initialization binds the trace to
the repository identity, the resolved change directory, and the current
immutable Git revision. It also records whether the workspace was dirty and the
digest of the evidence policy. The default policy has no trusted producers
configured, so it does not mark unconfigured stages verified. Use
`--policy <path>` to initialize with a versioned policy file.

## Ordinary apply and manual host inspection

The normal `/opsx:apply <change>` command and the managed apply skill are
unchanged. Running ordinary apply does not automatically invoke this local trace
skill, dispatch the nine personas, or capture Copilot host activity. Tracing is
opt-in: use the local `fabric-trace` skill, or run the CLI commands yourself. If
apply has already happened, a manually recorded event remains self-reported and
does not retroactively prove an invocation or validation.

For host activity that the CLI could not observe, inspect the relevant VS Code
Copilot Chat session and its visible tool/activity results (or a host-provided
session export, if available). Record only the activity you actually inspected;
do not paste prompts, full transcripts, or command output into the trace. For
example; replace the placeholder with the actual host session reference:

```powershell
$sessionRef = "session://<host-session-id>"
python scripts/fabric_trace.py record `
  --trace-dir $traceDir `
  --kind agent_invocation `
  --stage security `
  --summary "Manually inspected the host session for a security-review invocation" `
  --session-ref $sessionRef
```

The event is `self-reported`; the reference helps a human revisit the session
but is not host-verified evidence and cannot satisfy the security gate. If the
host does not expose enough information to confirm an activity, leave it
unrecorded rather than inferring it.

## Evidence policy and typed evidence

Policy files use `schemaVersion: 2` and `evidenceVersion: 1`. They define all
nine stages, the evidence types required at each stage, and trusted producers.
The following conservative policy mirrors the defaults: no producer is trusted,
so all gates remain missing or unverified until evidence is collected and
validated against an explicitly configured producer.

```json
{
  "schemaVersion": 2,
  "evidenceVersion": 1,
  "stages": {
    "proposal": {
      "requiredEvidence": ["planning-approval"],
      "trustedProducers": []
    },
    "design": {
      "requiredEvidence": ["planning-approval"],
      "trustedProducers": []
    },
    "implement": {
      "requiredEvidence": ["implementation-validation"],
      "trustedProducers": []
    },
    "test": { "requiredEvidence": ["test-results"], "trustedProducers": [] },
    "security": {
      "requiredEvidence": ["security-findings"],
      "trustedProducers": []
    },
    "legal": {
      "requiredEvidence": ["legal-assessment"],
      "trustedProducers": []
    },
    "review": {
      "requiredEvidence": ["review-approval"],
      "trustedProducers": []
    },
    "deploy": {
      "requiredEvidence": ["deployment-lineage"],
      "trustedProducers": []
    },
    "operate": {
      "requiredEvidence": ["operations-observation"],
      "trustedProducers": []
    }
  }
}
```

Evidence records carry `schemaVersion: 1`, an `evidenceType`, and fields
validated for that type. The accepted types are `planning-approval`
(revision-bound artifact SHA-256 hashes and attributable approval),
`implementation-validation` (source/tree revisions and named checks),
`test-results` (producer run/attempt, test counts, and coverage percentage),
`security-findings` (producer run/attempt, scanner names, and severity counts),
`legal-assessment` (risk level, triggers, assessment, and assessor),
`review-approval` (revision, reviewer, decision, and reference),
`deployment-lineage` (environment, artifact, deployed revision, and result), and
`operations-observation` (environment, artifact, timestamp, SLO state, and
observation result). Legal clearance is an optional typed field. A valid shape
does not itself establish trusted provenance or satisfy a gate.

## Stage contracts and outcomes

Each stage has a separate activity status and gate status. Activity means an
event was recorded for that stage; it does not mean the stage's evidence
contract was met. Gate evaluation uses the required typed evidence and trusted
producer in the trace policy. Labels, checked task boxes, successful process
exits, and free-text claims cannot replace that evidence.

| Stage     | Evidence required for a verified gate                                                                                                                                    |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| proposal  | Attributable approval bound to the proposal's current content hash.                                                                                                      |
| design    | Attributable approval bound to the current design, task-list, and delta-spec hashes.                                                                                     |
| implement | Validation evidence tied to the selected change and exact source/tree revision; task completion claims alone are insufficient.                                           |
| test      | Successful required test evidence, zero failed tests or errors, and measured coverage of at least 80 percent.                                                            |
| security  | All policy-required scanners completed, with no HIGH or CRITICAL findings.                                                                                               |
| legal     | An attributable, revision-bound risk assessment. Only accepted low-risk evidence can make this gate not-applicable; high-risk evidence also requires accepted clearance. |
| review    | An effective approval for the current revision, with no outstanding blocking changes request under policy.                                                               |
| deploy    | A real successful deployment with environment, immutable artifact/revision identifiers, smoke-test results, and verified lineage to the reviewed implementation.         |
| operate   | Successful post-deployment observation and SLO evidence for the same environment and artifact as the deployment.                                                         |

The report uses these gate outcomes:

| Gate outcome     | Meaning                                                                                                             |
| ---------------- | ------------------------------------------------------------------------------------------------------------------- |
| `missing`        | Required evidence is absent.                                                                                        |
| `running`        | A relevant command or evidence collection is still in progress or has no completion event.                          |
| `failed`         | Effective required evidence reports failure; earlier attempts remain in trace history.                              |
| `unverified`     | Evidence exists, but its producer, provenance, required fields, or prerequisite ordering cannot be verified.        |
| `stale`          | Evidence no longer matches the current artifact, workspace, revision, or deployed target.                           |
| `verified`       | Required evidence passed validation against the configured contract and applicable prerequisites.                   |
| `not-applicable` | Legal only: accepted, attributable evidence establishes a low-risk assessment. No other stage may use this outcome. |

“All stages observed” means all nine stages have activity events; it is not a
readiness result. A stage can be observed while its gate is missing, failed,
unverified, or stale. `verified-complete` requires every mandatory gate to be
`verified`, legal to be either `verified` or validly `not-applicable`, and the
evidence to satisfy prerequisite ordering: planning approvals before
implementation, implementation validation before test/security/legal/review,
those gates before deployment, and operations after the matching deployment.
Missing deployment or operations evidence prevents end-to-end completion even
when earlier stages are verified. Earlier traces are history only and do not
fill a current gate.

The default policy has no trusted producers. Until a producer is configured and
its evidence is validated, activity alone cannot make a gate verified. Read-only
GitHub collection, unified reports, and the synthetic lifecycle are implemented
and covered by focused tests. The mappings below identify the current test
coverage for each delta-spec scenario.

## Expected report output

Generate both report files from one evaluation. `report` prints the JSON path by
default; add `--format markdown` to print the Markdown path. `check` prints the
evaluated JSON and returns exit code `1` when the trace is incomplete:

```powershell
python scripts/fabric_trace.py report --trace-dir $traceDir
python scripts/fabric_trace.py report --trace-dir $traceDir --format markdown
python scripts/fabric_trace.py check --trace-dir $traceDir
$checkExitCode = $LASTEXITCODE
```

A real trace with no recorded activity has this shape (IDs, reasons, and
revision values vary; the report also includes repository, change directory,
policy digest, timeline, observation boundary, and next actions):

```markdown
# Fabric execution trace

- Status: **incomplete**
- Simulation: **No**
- Target revision: `<commit>`

| Stage     | Activity     | Gate    | Event IDs | Reasons |
| --------- | ------------ | ------- | --------- | ------- |
| proposal  | not-observed | missing | —         | ...     |
| design    | not-observed | missing | —         | ...     |
| implement | not-observed | missing | —         | ...     |
| test      | not-observed | missing | —         | ...     |
| security  | not-observed | missing | —         | ...     |
| legal     | not-observed | missing | —         | ...     |
| review    | not-observed | missing | —         | ...     |
| deploy    | not-observed | missing | —         | ...     |
| operate   | not-observed | missing | —         | ...     |
```

The persisted JSON has the same evaluated stage and timeline data, along with
the policy digest, target revision, observation boundary, next actions, and
simulation flag. A fixture-backed complete report instead says
`Simulation: YES — fixture-backed simulation, not a real deployment` in Markdown
and sets `"simulation": true` in JSON. That result demonstrates the evaluator
only; it is not evidence of a real deployment or operations run.

## Read-only GitHub collection

The collector uses `gh api --method GET` for GitHub REST requests and does not
change labels, post comments, approve pull requests, dispatch workflows, merge,
deploy, or archive. Before collecting, confirm the GitHub CLI is authenticated
for the intended host and account. `$traceDir` is the path captured during
initialization or supplied from a resumed trace:

```powershell
gh auth status --hostname github.com
$repository = "OWNER/REPOSITORY"
$prNumber = 123

python scripts/fabric_trace.py collect-github `
  --trace-dir $traceDir `
  --repo $repository `
  --pr $prNumber
python scripts/fabric_trace.py report --trace-dir $traceDir
python scripts/fabric_trace.py check --trace-dir $traceDir
```

The collection command requires read access to the repository and pull request.
For a fine-grained personal access token, grant only the repository permissions
needed by the endpoints being collected: **Actions: read**, **Pull requests:
read**, **Deployments: read**, and **Contents: read** when commit comparison is
needed for lineage. GitHub's required **Metadata: read** permission is also
needed for private repositories. Never grant write access for this collector or
place a token in a command, trace, or policy file. `gh auth status` checks the
configured CLI identity; it does not grant missing permissions. Collection
errors are persisted and returned as a nonzero result.

To trust structured workflow evidence, replace the `test` stage entry in the
example policy with a producer that matches the repository and exact workflow
path. The workflow must publish the named artifact with the selected JSON
member. This example shows only the test stage; other stages still need their
own explicitly configured contracts:

```json
"test": {
  "requiredEvidence": ["test-results"],
  "trustedProducers": [{
    "id": "ci-test-results",
    "type": "github-actions",
    "repository": "OWNER/REPOSITORY",
    "workflow": ".github/workflows/ci.yml",
    "requiredJobs": ["test"],
    "evidenceArtifacts": [{
      "artifactName": "fabric-trace-evidence",
      "archivePath": "evidence/test-results.json",
      "evidenceType": "test-results"
    }]
  }]
}
```

The selected evidence must be a valid `test-results` record whose
`sourceRevision`, `producerRun.runId`, and `producerRun.attempt` match the trace
revision and the collected workflow run attempt. Only explicitly selected
artifacts are downloaded; paths and archive sizes are bounded and validated. The
current SDLC orchestrator does not publish this structured artifact, so the
example requires a producer workflow that does.

Collection appends new observations rather than replacing trace history. Rerun
`collect-github` after provider evidence changes, then regenerate the report. A
collection failure is visible and prevents earlier cached evidence from silently
satisfying the gate. A new implementation revision needs a new trace, optionally
linked with `--predecessor`; recollecting cannot change the revision bound to an
existing trace.

The SDLC orchestrator is separate from the collector. Its issue intake is
triggered by an issue being labeled; its pull-request workflow is triggered by
`labeled`, `unlabeled`, and `ready_for_review`. The test stage gate itself runs
only when a pull request receives the `stage:test` label, so it is not an
automatic test-on-every-push workflow. Its Python command enforces an 80%
coverage threshold and its selected test commands fail the job on command
errors; they are not configured as warning-only steps. However, the .NET path
collects coverage without enforcing an 80% threshold, and the orchestrator does
not publish the structured, revision/run/attempt-bound evidence artifact
required by this trace policy. A green job, status comment, warning, or label
alone therefore cannot verify the trace's test gate. The orchestrator also has
write permissions for its own comments and labels; these are not needed by the
read-only trace collector.

Sources:

- [`sdlc-orchestrator.yml`](../.github/workflows/sdlc-orchestrator.yml) —
  current event filters, permissions, and test-stage behavior.
- [GitHub CLI `gh auth status`](https://cli.github.com/manual/gh_auth_status)
  and [`gh api`](https://cli.github.com/manual/gh_api) — authentication check
  and REST request interface.
- [Fine-grained token permission requirements](https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens).
- GitHub REST endpoints:
  [pull requests](https://docs.github.com/en/rest/pulls/pulls#get-a-pull-request),
  [workflow runs](https://docs.github.com/en/rest/actions/workflow-runs#list-workflow-runs-for-a-repository),
  [jobs for a workflow run attempt](https://docs.github.com/en/rest/actions/workflow-jobs#list-jobs-for-a-workflow-run-attempt),
  [artifacts](https://docs.github.com/en/rest/actions/artifacts#list-workflow-run-artifacts),
  [pull request reviews](https://docs.github.com/en/rest/pulls/reviews#list-reviews-for-a-pull-request),
  [deployments](https://docs.github.com/en/rest/deployments/deployments#list-deployments),
  [deployment statuses](https://docs.github.com/en/rest/deployments/statuses#list-deployment-statuses),
  and
  [commit comparison](https://docs.github.com/en/rest/commits/commits#compare-two-commits).

## Delta-spec scenario-to-test mapping

Scenario titles correspond to the delta spec. Each row maps to focused tests
that currently exercise the behavior.

| Delta-spec scenario                            | Test mapping                                                                                                                                                                                                                                                                                       |
| ---------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Same slug in different planning directories    | Current: `test_fabric_trace_identity.py::TraceIdentityTests.test_duplicate_slug_requires_explicit_directory`                                                                                                                                                                                       |
| Evidence from another revision                 | Current: `test_fabric_trace_identity.py::TraceIdentityTests.test_mismatched_revision_and_repository_are_rejected`                                                                                                                                                                                  |
| Apply skill loaded without security invocation | Current: `test_fabric_trace_record.py::TraceRecordTests.test_manual_activity_kinds_are_distinct_and_self_reported`; `test_fabric_trace_policy.py::TracePolicyTests.test_unconfigured_producer_and_untrusted_provenance_fail_closed`                                                                |
| Validation command fails                       | Current: `test_fabric_trace_run.py::TraceRunTests.test_nonzero_exit_is_recorded_and_returned`                                                                                                                                                                                                      |
| Process stops before a completion event        | Current: `test_fabric_trace_run.py::TraceRunTests.test_missing_completion_remains_running_not_successful`                                                                                                                                                                                          |
| Fabricated success event                       | Current: `test_fabric_trace_record.py::TraceRecordTests.test_fabricated_success_and_session_reference_do_not_satisfy_gates`                                                                                                                                                                        |
| No deployment configured                       | `test_fabric_trace_lifecycle.py::FabricTraceLifecycleTests.test_missing_deploy_and_operate_evidence_prevents_completion`                                                                                                                                                                           |
| Green test job masks failures                  | Current: `test_fabric_trace_policy.py::TracePolicyTests.test_labels_checked_tasks_and_green_jobs_do_not_replace_typed_evidence`; `test_fabric_trace_policy.py::TracePolicyTests.test_test_coverage_below_threshold_fails_gate`                                                                     |
| Security or review evidence is insufficient    | Current: `test_fabric_trace_policy.py::TracePolicyTests.test_missing_required_security_scanner_and_high_findings_fail_gate`; `test_fabric_trace_github.py::TraceGitHubCollectionTests.test_collects_all_attempts_steps_artifacts_and_deployment_statuses`.                                         |
| No assessment recorded                         | `test_fabric_trace_lifecycle.py::FabricTraceLifecycleTests.test_missing_legal_assessment_remains_missing`                                                                                                                                                                                          |
| High-risk assessment without clearance         | Current: `test_fabric_trace_policy.py::TracePolicyTests.test_high_risk_legal_assessment_requires_clearance`                                                                                                                                                                                        |
| Push after successful tests                    | Current: `test_fabric_trace_policy.py::TracePolicyTests.test_local_evidence_is_stale_after_dirty_implementation_command`                                                                                                                                                                           |
| Unrelated successful deployment                | Current: `test_fabric_trace_github.py::TraceGitHubCollectionTests.test_unrelated_successful_deployment_remains_unverified`; `test_fabric_trace_policy.py::TracePolicyTests.test_operations_evidence_must_match_deployed_artifact`.                                                                 |
| Required job was skipped                       | Current: `test_fabric_trace_github.py::TraceGitHubCollectionTests.test_collects_all_attempts_steps_artifacts_and_deployment_statuses`.                                                                                                                                                             |
| API access denied                              | Current: `test_fabric_trace_github.py::TraceGitHubCollectionTests.test_collection_failures_are_persisted_and_return_nonzero`; `test_fabric_trace_github.py::TraceGitHubCollectionTests.test_collection_failure_invalidates_previously_verified_evidence`.                                          |
| Report requested from an incomplete trace      | `test_fabric_trace_record.py::TraceRecordTests.test_reports_share_partial_evaluation_and_include_required_details`; `test_fabric_trace_record.py::TraceRecordTests.test_report_and_check_return_explicit_invalid_trace_errors`                                                                     |
| Full synthetic lifecycle                       | `test_fabric_trace_lifecycle.py::FabricTraceLifecycleTests.test_simulated_full_lifecycle_is_complete_and_marked_in_both_reports`                                                                                                                                                                   |
| Command includes a credential                  | Current: `test_fabric_trace_run.py::TraceRunTests.test_child_output_is_visible_but_never_persisted`; `test_fabric_trace_record.py::TraceRecordTests.test_metadata_allowlist_rejects_raw_fields_and_secret_values`                                                                                  |
| Skill invoked outside the trace wrapper        | `test_fabric_trace_skill.py::FabricTraceSkillTests.test_documented_local_flow_uses_temporary_repository` verifies the flow remains incomplete; `test_fabric_trace_record.py::TraceRecordTests.test_reports_share_partial_evaluation_and_include_required_details` checks the observation boundary. |

## Resume an existing trace

To continue recording activity against the same target revision, use the
existing trace directory rather than initializing another trace. For example,
the following records a self-reported claim; it is not proof that the stage ran
or passed:

```powershell
python scripts/fabric_trace.py record `
  --trace-dir $traceDir `
  --kind stage_claim `
  --stage implement `
  --summary "Implementation work continued"
```

Use `report` or `check` with the same `--trace-dir` to inspect its current
status. If the implementation commit changes, initialize a new trace for the new
revision and link the previous trace with `--predecessor <traceId>`. Previous
trace history is a reference only: gate success is not carried forward without
revalidation.

## Record activity and observe a command

Use `record` for manually reported activity. Supported kinds are
`instruction_discovery`, `instruction_inclusion`, `skill_load`,
`agent_invocation`, and `stage_claim`. For example:

```powershell
python scripts/fabric_trace.py record `
  --trace-dir $traceDir `
  --kind skill_load `
  --stage implement `
  --summary "Loaded the local fabric-trace skill"
```

Manual records are always `self-reported`; they cannot set a trusted provenance
or gate status. A session reference or URL is only a reference, not
verification.

Use `run` to execute one local command as an argument array after `--`:

```powershell
python scripts/fabric_trace.py run `
  --trace-dir $traceDir `
  --stage test `
  --summary "Run a harmless local command" `
  -- python -c "print('example output stays with caller')"
```

The trace records the observed start/completion, exit code, and workspace and
revision state. The child process's stdout and stderr remain available to the
caller but are not saved in the trace. A zero exit code means only that this
process exited successfully; it does not establish that tests, coverage, or
another validation gate passed. Gates require the structured evidence and
trusted producer configured by policy. Inspect `report` or `check` for the
actual gate status.

## Data-sharing precautions

Trace files are ignored by Git, but that does not make their contents safe to
share. Keep summaries and any optional metadata free of credentials, personal or
sensitive information, raw prompts, source contents, environment values, and
command output. Command arguments are not persisted and credential-shaped
arguments are rejected, but free text can still contain sensitive details;
sanitization is not a guarantee that arbitrary text is secret-free. Before
sharing a trace, report, or evidence file, review it, remove unnecessary
sensitive details, and share only the minimum needed.

## Trace files and storage boundary

Each trace directory contains:

- `trace.json`: schema version, trace UUID, repository identity, change
  directory, target revision, creation time, dirty-at-initialization flag,
  policy digest, optional predecessor UUID, simulation flag, and references.
- `events.jsonl`: append-only, versioned activity and evidence events, including
  event and invocation identifiers, stage, kind, timestamp, provenance, summary,
  target revision, and evidence references.
- `policy.json`: the versioned evidence policy used for evaluation.
- `evidence/`: normalized, allowlisted evidence metadata and small
  machine-readable reports; raw logs are not stored by default.
- `report.json` and `report.md`: generated views of the same evaluated result.

Runtime files belong only under the repository's `.fabric-traces/` directory,
which is ignored by Git. The CLI validates that trace files remain inside the
canonical trace directory. Treat reports and evidence as local working data;
review them for sensitive information before sharing.

## Retention and targeted rollback

Trace output is local, Git-ignored working data. The CLI does not automatically
purge it. Retain only the traces needed for review; before copying one
elsewhere, inspect its summaries, references, and evidence for sensitive
information. Deleting a trace is permanent. To remove one identified trace,
resolve and check that exact directory first, then confirm the targeted removal:

```powershell
$traceRoot = (Resolve-Path -LiteralPath ".fabric-traces").Path
$resolvedTrace = (Resolve-Path -LiteralPath $traceDir).Path
$tracePrefix = $traceRoot.TrimEnd('\') + '\'
if (-not $resolvedTrace.StartsWith(
    $tracePrefix, [System.StringComparison]::OrdinalIgnoreCase
)) { throw "Refusing to remove a path outside .fabric-traces." }
if (-not (Test-Path -LiteralPath (Join-Path $resolvedTrace "trace.json"))) {
  throw "The selected directory is not a trace."
}
Remove-Item -LiteralPath $resolvedTrace -Recurse -Confirm
```

To roll back the local pilot implementation, review `git status --short` and
`git diff -- .gitignore`, then revert only the pilot-owned files and the exact
`.fabric-traces/` ignore entry through the normal reviewed change process.
Preserve unrelated and pre-existing worktree changes. Do not use `git clean`,
wildcards, or a broad repository reset as a cleanup shortcut.

## Trust limitation

These files are stored on the workstation and are not a cryptographic audit log.
A person or process able to modify the local trace files or collector can tamper
with them. Provenance and external-source references are checked by the pilot,
but local records remain self-reported unless a trusted collector validates
them. A session reference may help a human inspect activity; it does not by
itself verify execution or satisfy a gate.
