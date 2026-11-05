---
applyTo: "openspec/**"
---

# OpenSpec Workflow Instructions

When working with files in `openspec/`, always follow the OpenSpec workflow
(<https://github.com/Fission-AI/OpenSpec>).

## Command Skills

Apply the Pre-Capture Intake Decision below before any setup or capture write.
Read-only assessment needs no repository initialization.

Use the shared OpenSpec command skills for new workflows. Core Commands
(/opsx:_) are the legacy interface. Only use Core Commands (/opsx:_) when the
user types the literal `/opsx:` command syntax; otherwise always use Command
Skills. Command Skills require a working OpenSpec CLI. If the CLI is already
installed and `openspec/` is already initialized, skip installation and proceed
directly to `openspec context --json`. Otherwise, install and initialize the
CLI:

```powershell
npm install -g @fission-ai/openspec@latest
openspec init
openspec context --json
```

Before running `openspec init`, back up `openspec/config.yaml` if it exists.
After initialization completes, restore any repository-specific fields that
`openspec init` overwrote.

| Legacy prompt            | Command skill             |
| ------------------------ | ------------------------- |
| `opsx-propose.prompt.md` | `openspec-propose`        |
| `opsx-apply.prompt.md`   | `openspec-apply-change`   |
| `opsx-verify.prompt.md`  | `openspec-verify-change`  |
| `sdlc-kickoff.prompt.md` | `software-fabric-kickoff` |

### Stop Conditions

If any of the following conditions occur, stop and report as described. Do not
modify artifacts and do not fall back to a deprecated prompt wrapper.

| #   | Condition                                                                                             | Required message                                                                                                                             | Modify artifacts? |
| --- | ----------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- | ----------------- |
| 1   | `npm install -g @fission-ai/openspec@latest` fails                                                    | Report the exact installation error                                                                                                          | No                |
| 2   | Installed CLI version conflicts with the existing `config.yaml` schema version                        | Report the version mismatch. If `config.yaml` does not yet exist, proceed with a fresh `openspec init` and skip this version-conflict check. | No                |
| 3   | CLI command is not found, or `openspec context --json` fails to resolve a valid `openspec/` root path | Report the setup requirement                                                                                                                 | No                |
| 4   | A legacy prompt has no corresponding command skill in the table above                                 | Report that no migration path exists                                                                                                         | No                |
| 5   | A MODIFIED or REMOVED requirement name does not exist in the main spec (see On Archive)               | Report the mismatch instead of archiving                                                                                                     | No                |
| 6   | Any Quality Gate Checklist item is unmet (see below)                                                  | Report which items are unmet                                                                                                                 | No                |

If only some legacy prompts lack a migration path, proceed with the ones that do
and report only the missing ones.

If `openspec context --json` succeeds but returns an unrecognized schema
version, treat this the same as Stop Condition #2.

## Core Commands

| Command                 | Effect                                                 |
| ----------------------- | ------------------------------------------------------ |
| `/opsx:propose <slug>`  | Create a new change folder with all planning artifacts |
| `/opsx:explore [topic]` | Investigate and think through ideas before proposing   |
| `/opsx:apply [slug]`    | Implement tasks from `tasks.md`                        |
| `/opsx:sync [slug]`     | Preview-merge delta specs into main specs              |
| `/opsx:archive [slug]`  | Merge deltas into specs/ and move change to archive/   |

## File Locations

- **Source of truth specs:** `openspec/specs/<domain>/spec.md`
- **In-flight changes:** `openspec/changes/<slug>/`
- **Archived changes:** `openspec/changes/archive/<date>-<slug>/`
- **Config:** `openspec/config.yaml`

## Delta Spec Format

When creating `specs/<domain>/spec.md` inside a change folder, use ADDED /
MODIFIED / REMOVED sections:

```markdown
# Delta for <domain>

## ADDED Requirements

### Requirement: <Name>

<Description using MUST/SHALL/SHOULD language>

#### Scenario: <scenario name>

- GIVEN <precondition>
- WHEN <action>
- THEN <expected outcome>

## MODIFIED Requirements

### Requirement: <Existing Requirement Name>

<Updated description>
(Previously: <what it said before>)

## REMOVED Requirements

### Requirement: <Name>

(Removed because: <reason>)
```

## On Archive

- The domain name is taken from the delta spec folder path
  `openspec/changes/<slug>/specs/<domain>/spec.md`.
- Sync every delta into its main spec and verify the resulting requirements and
  scenarios before moving the change. Already-synced deltas still require content
  verification. A sync blocker, excluded delta, or failed comparison blocks the
  entire affected change, including in bulk archive.
- Never offer archive without syncing or use confirmation to override required
  completion, quality gates, or sync verification. Report partial sync writes on
  failure; keep the change active and do not claim rollback.

## Pre-Capture Intake Decision

Before any repository write for a new idea or draft proposal, assess it in
conversation or session storage outside the worktree. Offer one decision:
**Proceed**, **Defer**, or **Do not pursue**. A raw idea, issue label, P0 priority,
or kickoff alone is not capture authorization. An explicit request to create
named repository artifacts counts as Proceed; do not ask the same decision again
when handing off between skills. Missing input keeps capture paused.

Defer or Do not pursue ends intake without repository writes: no initialization,
change directory, metadata, proposal, specs, design, tasks, or code. Report that
the idea was deferred or not pursued, not delivered or successfully archived.
No delivery gates are needed merely to end intake. Do not run archive or sync,
mark tasks complete, or delete/revert existing work; cleanup of an already
captured proposal requires separate explicit authorization.

Proceed permits capture, not acceptance of the resulting proposal/spec or
implementation. Apply the mandatory planning and archive gates below after
capture. This is a conversational exit, not a CLI skip command, `skip_specs`
waiver, new stage, or alternate successful archive path.

## Mandatory Planning Contract

### Conditional UX Planning

Each proposal must include `## UX Applicability` with exactly one fenced JSON
object containing boolean `required` and a nonempty scope-backed `reason`.
Only changes affecting a visual interface require the UX Designer stage and
`ux-brief.md` before architecture. Preserve the brief's stable criterion IDs
in design, delta scenarios, and QA tasks.

CLI-only, API-only, and framework changes with no affected visual interface
require no UX stage, brief, UX-specific specs, validation report, UX tests, or
frontend tooling. Route accepted nonvisual proposals directly to architecture.
Their normal functional specs, tests, and all other applicable gates remain
required. Mixed changes limit UX work to affected visual surfaces.
Missing or conflicting applicability pauses the handoff; do not infer it from
missing artifacts or the mere presence of frontend files. Scope changes require
renewed acceptance. This exemption never waives normal OpenSpec planning.

### Required Artifacts and Acceptance

Before implementation, require a substantively complete proposal, delta specs
for every affected domain, design, and ordered tasks. The proposal must be
accepted before design begins; the current proposal/spec must have explicit
acceptance evidence before implementation. Use existing conversation approval
or linked review evidence tied to the current content, not a new approval format.
Missing or stale evidence blocks implementation.

Resolve required artifact roles through the selected schema's status and context
paths, including the transitive dependencies of `applyRequires`. These Software
Fabric roles remain mandatory even if the schema omits them or reports them
`skipped`; `skip_specs` is not a waiver. Stop on ambiguous mappings instead of
guessing filenames or writing an artifact explicitly marked skipped.
CLI readiness and file existence alone do not prove substantive completeness or
acceptance. Genuinely optional artifacts outside these required roles retain
warnings and do not become mandatory gates.

An implementation request authorizes work only after these prerequisites pass.
Never pre-check tasks to satisfy a PR-progress condition. If planning changes
invalidate acceptance, pause affected implementation until acceptance is renewed.

## Quality Gate Checklist (before archive)

- [ ] Required planning artifacts are complete and current acceptance is verified.
- [ ] All tasks in `tasks.md` are complete.
- [ ] All new scenarios have passing tests.
- [ ] No removed requirements are still referenced elsewhere.
- [ ] All CI checks are green (build, lint, unit tests).
- [ ] Security review has passed with no HIGH or CRITICAL findings.
- [ ] New-code coverage is at least 80%.
- [ ] At least one code-review approval (human or AI) is present.
- [ ] All spec acceptance criteria are satisfied.
- [ ] Required legal review is approved for changes with legal-risk triggers.
- [ ] Applicable operational archive criteria are met: SLOs, alerts, runbooks,
      stability window, and post-mortem completion when required.

If any checklist item cannot be verified due to missing data, treat it as unmet
and report which items could not be verified. Check these gates before any
archive-driven sync writes or moves, for each change in a batch. Non-applicability
must be grounded in the change's actual scope (for example no new code for a
coverage metric), not inferred from missing evidence or a confirmation.
Local artifact validation does not certify external quality gates.

If any Quality Gate Checklist item is unmet, do not run `/opsx:archive` (see
Stop Conditions #6). User confirmation cannot override mandatory gates.
