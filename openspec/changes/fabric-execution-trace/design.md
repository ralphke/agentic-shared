# Design

## Context

See [proposal.md](./proposal.md) for motivation and
[the capability delta](./specs/fabric-execution-tracing/spec.md) for the
behavior contract.

Observed constraints:

- `.github/instructions/sdlc-fabric.instructions.md` guides agent behavior; it
  does not execute a stage dispatcher.
- Both the current apply skill and prompt implement an OpenSpec task loop, not
  an automatic persona pipeline. They have existing uncommitted edits that must
  remain untouched.
- `sdlc-orchestrator.yml` reacts to issue labels and PR
  labeled/unlabeled/ready-for-review events. The test gate is label-triggered,
  not push-triggered. Its Python test command fails hard and enforces 80%
  coverage; the .NET command fails hard but only collects coverage. Neither test
  command is warning-only, and the workflow does not publish the structured
  evidence artifact required by the trace policy.
- `ci.yml` validates workshop structure; a green CI result is not evidence of
  application test coverage.
- `openspec-archive-gate.yml` references
  `.github/scripts/validate_openspec_change.py`, but no `.github/scripts/`
  implementation was found. Do not depend on this gate for trace validation.
- The manifest reserves local skill extensions and marks workflows managed. No
  new hosted workflow is needed for the local pilot.
- CLI context resolves `openspec/`, with an empty main-spec inventory.
  Historical Fabric requirements under `spec/openspec/` describe broader
  behavior but are not the CLI's current main-spec store.

This is cross-cutting evidence modeling and trust-boundary work, so design is
required rather than conditionally skipped.

## Goals / Non-Goals

**Goals:**

- One correlation ID and report across local implementation and GitHub evidence.
- Separate observed activity, evidence provenance, and validated gate outcomes.
- Make partial traces useful and honest before every stage is instrumented.
- Keep the pilot executable on Windows and Linux with Python standard library,
  Git, and `gh`.

**Non-Goals:**

- Automatic scheduling of every persona, deployment provisioning, or operations
  setup.
- Changing generic apply behavior, modifying upstream assets, or enforcing
  branch protection.
- Claiming all host activity is captured, or claiming unsigned local records are
  tamper-proof.
- Treating a successful process, agent statement, label, or arbitrary Markdown
  report as proof that business requirements were met.
- Adding a telemetry backend, collecting raw conversations, or retroactively
  inventing stage executions.

## Decisions

### 1. Explicit local tracing entry point

Implement `scripts/fabric_trace.py` with `init`, `record`, `run`,
`collect-github`, `report`, and `check` subcommands. Add
`.github/skills/local/fabric-trace/SKILL.md` as the opt-in assistant entry
point.

The local skill initializes or resumes the trace, invokes the existing apply
skill explicitly, uses the command runner for validation, collects available
GitHub evidence when a PR exists, and reports coverage gaps. It does not imply
that the apply invocation runs every Fabric stage. Record a skill/subagent
invocation as self-reported unless a host execution reference is available and
validated; a local skill cannot independently observe all host events.

Prefer this wrapper over editing managed instructions or installing
host-specific hooks. Hooks could improve coverage later, but would require a
separately approved host integration. The guide must document both the wrapper
entry point and explicit CLI use after an ordinary apply.

### 2. Versioned trace envelope with an immutable target per trace

Store runtime files under `.fabric-traces/<trace-id>/`, adding an exact ignore
entry. Use:

- `trace.json`: schema version, UUID, repository identity, resolved change
  directory, target commit, creation time, optional PR/session references,
  simulation flag, and evidence-policy digest.
- `events.jsonl`: append-only versioned events with unique event and invocation
  IDs, stage, event kind, UTC timestamp, provenance, safe summary, target
  revision, and evidence references.
- `evidence/`: normalized allowlisted metadata and small machine-readable
  reports; no raw logs by default.
- `report.json` and `report.md`: generated from the same evaluated result, with
  generated time and evidence freshness information.

Require `--change-dir` instead of resolving a slug against competing directory
trees. Check existence and containment, and fail on ambiguous or unsafe paths.

Bind a trace to a committed revision. Local activity on a dirty workspace can be
recorded with a dirty marker but cannot satisfy a gate for that commit. After an
implementation commit changes, initialize a new trace with a predecessor link.
Carry history as references, never carry forward gate success without
revalidation. This avoids silently mutating the meaning of older evidence.

Use exclusive short-lived write locking and atomic replacement of generated
files; reject concurrent conflicting writes. A truncated event line or stale
lock must produce a diagnostic, not be silently discarded.

### 3. Evidence has a source and a trust level

Keep these dimensions separate:

| Evidence class             | What it can establish                                                                              | What it cannot establish alone                         |
| -------------------------- | -------------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| Collector-observed command | The specified process started and returned its recorded exit code in the recorded workspace        | Test coverage, semantic correctness, or agent identity |
| Provider-verified evidence | GitHub authenticated metadata identifies a matching run/job/review/deployment and accepted reports | Unobserved activity outside those producers            |
| Self-reported event/import | An actor asserted or supplied a claim                                                              | Verified execution or gate completion                  |

`record` cannot set trusted provenance or directly mark a gate verified. Only
collectors create observed records; gate evaluation revalidates their source
references, identifiers, revision, and required report fields. Local records
remain within the workstation trust boundary: someone able to modify the
collector or its files can tamper with them. Call this limitation out in both
the guide and reports; do not describe the trace as a cryptographic audit log.

An exported session reference can help a human inspect agent activity, but the
pilot does not parse arbitrary host log formats or automatically promote them to
trusted evidence.

### 4. Explicit stage contracts instead of green-label inference

Use a versioned JSON policy supplied at initialization and stored with its
digest. Document its schema and provide a conservative example in the guide. It
maps each stage to evidence types, expected workflow paths and job/step names
where applicable, required report fields, and permitted approver
identities/roles.

Do not generate permissive contracts from whatever jobs happen to exist. An
absent producer or unconfigured stage remains missing. Changing policy requires
a new trace; reports expose the policy digest.

Minimum stage contracts:

| Stage     | Required evidence                                                                                                                           |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| proposal  | Proposal artifact hash plus attributable approval of that exact artifact                                                                    |
| design    | Design, tasks, and delta-spec hashes plus attributable approval of those artifacts                                                          |
| implement | Exact commit/tree tied to the selected change, task-to-change summary, and implementation validation evidence; checkboxes alone do not pass |
| test      | Successful required test execution plus machine-readable counts, zero failures/errors, and measured coverage >=80 percent                   |
| security  | Successful required scanners plus structured findings summary with zero HIGH/CRITICAL and no omitted required scanner                       |
| legal     | Revision-bound risk assessment and low-risk rationale, or high-risk assessment with clearance from the accepted reviewer                    |
| review    | Current effective approval for the reviewed revision, with no outstanding blocking changes request under policy                             |
| deploy    | Successful real deployment, environment and immutable artifact/revision identifiers, smoke-test results, and verified source lineage        |
| operate   | Monitoring/SLO configuration and a successful post-deployment observation for the same environment and artifact                             |

Define a minimal, versioned evidence JSON format for approvals, coverage,
findings, assessments, deployment, and operations. Required fields must be typed
and validated, not inferred from prose. Reports from GitHub artifacts must be
associated with the configured successful producer run and attempt; downloading
arbitrary JSON does not establish trusted provenance.

For artifact approvals and legal assessments, use provider-verifiable attributed
references bound to immutable artifact hashes/revisions. A manually supplied
local report remains self-reported until its provenance is verified against the
policy. This can deliberately leave proposal/design/legal incomplete in an early
pilot.

Stage reports expose independent activity and gate status. Gate states are
`missing`, `running`, `failed`, `unverified`, `stale`, `verified`, and
`not-applicable`. Only legal supports not-applicable, and only from accepted
low-risk evidence. Terminal failures cannot be hidden by a later unrelated
success; later accepted reruns can supersede the same failed check while
retaining both attempts.

Overall `verified-complete` requires every mandatory stage verified, legal
verified or validly not-applicable, and valid ordering: approvals precede
implementation; tests/security/legal/review cover the reviewed content before
deploy; operate follows that deployment. An early deployment remains visible but
does not satisfy ordered completion. A trace can show all stages observed
without qualifying as verified-complete.

### 5. Read-only GitHub collector with exact source correlation

Use `gh api` via an argument array and no shell interpolation. Retrieve
paginated PR metadata, run attempts, jobs and steps, effective reviews, artifact
metadata, and deployment/status references. Fetch only explicitly selected small
evidence artifacts with size and path limits.

Validate repository identity, PR head SHA, workflow path, policy-selected
jobs/steps, conclusion, attempt number, and evidence revision. Handle retries by
run ID and attempt, not display name alone. Treat skipped/cancelled jobs as
non-passing. Expose API errors, expired artifacts, access limitations, and
missing producers; do not treat an empty response as success.

For merge commits or deployed artifacts with another identifier, require
verifiable Git/tree or artifact lineage to the reviewed source revision. A
deployment URL or successful run with a different SHA is insufficient.

The collector must not post comments, change labels, approve PRs, dispatch
workflows, merge, deploy, or archive. Do not assume label changes made by
workflow tokens will trigger downstream workflows.

### 6. Minimal data and explicit outcomes

`run` receives the command as an argument array after `--`, records a safe
executable/operation summary, and does not store raw arguments, environment, or
stdout/stderr. Output stays available to the caller; parsed allowlisted result
fields become evidence. Validate supported evidence inputs and redact
credential-shaped values in free text before persistence. Document that
arbitrary free text cannot be guaranteed secret-free and must not contain
secrets.

Escape untrusted values in Markdown and reject unsafe URL schemes. Reject
malformed or unsupported-version events rather than silently defaulting values.
Persist collection failures as failures. Return nonzero for command failure,
invalid input, collection error, and incomplete `check`; `report` can render an
incomplete trace successfully but must show its incomplete status.

Both reports include the stage table, activity timeline, source references,
trust classification, policy digest, target revision, observation limitations,
and next evidence needed. A simulation flag is sticky and visible;
fixture-backed success is never presented as real-world success.

## Risks / Trade-offs

- [No existing producer emits all required reports] -> Keep stages incomplete
  and list missing evidence; do not broaden this pilot into an unapproved
  deployment project.
- [Managed apply has no trace extension point] -> Use an opt-in local wrapper
  and disclose that plain apply has no automatic trace coverage.
- [Local file edits can falsify events] -> Separate provenance, revalidate
  external sources, and state the workstation trust boundary; signed
  attestations are out of scope.
- [Old Fabric docs imply stronger gates] -> Explain the difference in the new
  guide without rewriting managed assets.
- [Private metadata in exports] -> Minimize stored fields, ignore local output,
  and require review before sharing reports.
- [GitHub job success hides warnings or skipped work] -> Require structured
  results and policy-selected non-skipped steps.
- [Two OpenSpec trees] -> Use CLI-resolved paths and explicit directory
  identity; do not migrate either tree in this change.

## Migration Plan

1. Add the local script, focused tests, local skill, guide, and runtime ignore
   entry.
2. Validate all requirements with deterministic fixtures and mocked GitHub
   responses; no network or credentials required for the automated suite.
3. Run a real local pilot for a committed revision, collecting only available
   evidence. Confirm missing deploy/operate producers prevent verified
   completion.
4. Demonstrate synthetic full-lifecycle output separately, visibly marked
   simulation.
5. Keep normal apply and existing workflows untouched. Rollback removes the
   pilot files and exact ignore entry; retain or explicitly remove individual
   trace directories only on user request.

No production deployment is part of rollout. Completing this tooling change does
not itself prove that every Fabric stage ran on a real application.
