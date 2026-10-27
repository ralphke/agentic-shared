# Proposal

## Why

Software Fabric instructions describe stage obligations, but OpenSpec task
completion, PR labels, agent activity, and GitHub checks currently provide
disconnected evidence. Participants need one inspectable execution trace that
shows what actually ran, which revision it covered, and which stages are still
missing evidence.

## What Changes

- Add an opt-in, repo-local trace with one correlation ID linking the OpenSpec
  change path, implementation revision, agent-session references, PR, workflow
  runs, and stage evidence.
- Record actual command executions, explicitly observed skill/subagent
  invocations, and read-only GitHub evidence collection. Distinguish discovered
  instructions, loaded skills, invoked agents, and successful validation.
- Generate machine-readable JSON and a readable Markdown stage report from the
  same validated evidence, covering proposal, design, implement, test, security,
  legal, review, deploy, and operate.
- Fail closed for missing, failed, stale, inaccessible, or merely self-reported
  evidence. Permit legal not-applicable only with an explicit attributable risk
  assessment; do not infer stage success from labels or checked tasks.
- Add a local implementation skill wrapper and monitoring guide without changing
  managed apply skills, personas, instructions, or workflows. Ordinary OpenSpec
  apply remains unchanged; the wrapper provides the opt-in traced entry point.
- Test positive and negative evidence paths, including a synthetic
  full-lifecycle fixture clearly identified as a simulation rather than a real
  deployment.

## Capabilities

### New Capabilities

- `fabric-execution-tracing`: Correlated, evidence-qualified recording and
  reporting of Software Fabric stage execution and readiness.

### Modified Capabilities

None in the CLI-resolved `openspec/specs/` inventory. Historical Fabric specs
under `spec/openspec/specs/` remain reference material; this change does not
migrate or overwrite them.

## Impact

- Proposed implementation surfaces: `scripts/fabric_trace.py`, focused
  standard-library tests and fixtures,
  `.github/skills/local/fabric-trace/SKILL.md`, and
  `doc/fabric-execution-trace.md`.
- Persistent runtime output goes to an explicit Git-ignored local output
  directory, not committed planning files; a targeted `.gitignore` entry is
  included if needed.
- Use Python standard library and the existing `gh` CLI; GitHub collection
  requires read access only. No telemetry service, hosted database, automatic
  deployment, label advancement, or branch-protection changes.
- The CLI currently resolves `openspec/`, while older Fabric assets use
  `spec/openspec/`. Bind traces to an explicit resolved change directory and do
  not guess by slug.
- Shared assets remain upstream-owned. The pilot must not modify the existing
  uncommitted OpenSpec customizations or silently claim that generic apply now
  orchestrates every persona.
- Acceptance: all stages appear in a single report; stage claims cite verifiable
  revision-bound evidence; missing deployment/operations evidence prevents an
  end-to-end success claim; a real pilot reports its actual partial state.
- Legal risk assessment: low-risk local development tooling with no new external
  data processor or production data access. Exported metadata may include
  repository paths, actor identifiers, and private URLs; minimize collection,
  avoid raw prompts/source/secrets, and require a deliberate assessment for each
  traced change.
