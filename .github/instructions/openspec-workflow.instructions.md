---
applyTo: "openspec/**"
---

# OpenSpec Workflow Instructions

When working with files in `openspec/`, always follow the OpenSpec
workflow (https://github.com/Fission-AI/OpenSpec).

## Command Skills

Use the shared OpenSpec command skills for new workflows. Core Commands (/opsx:*) are
the legacy interface. Only use Core Commands (/opsx:*) when the user types the literal
`/opsx:` command syntax; otherwise always use Command Skills. Command Skills require a
working OpenSpec CLI. If the CLI is already installed and `openspec/` is already
initialized, skip installation and proceed directly to `openspec context --json`.
Otherwise, install and initialize the CLI:

```powershell
npm install -g @fission-ai/openspec@latest
openspec init
openspec context --json
```

Before running `openspec init`, back up `openspec/config.yaml` if it exists. After
initialization completes, restore any repository-specific fields that `openspec init`
overwrote.

| Legacy prompt | Command skill |
|---|---|
| `opsx-propose.prompt.md` | `openspec-propose` |
| `opsx-apply.prompt.md` | `openspec-apply-change` |
| `opsx-verify.prompt.md` | `openspec-verify-change` |
| `sdlc-kickoff.prompt.md` | `software-fabric-kickoff` |

### Stop Conditions

If any of the following conditions occur, stop and report as described. Do not modify
artifacts and do not fall back to a deprecated prompt wrapper.

| # | Condition | Required message | Modify artifacts? |
|---|---|---|---|
| 1 | `npm install -g @fission-ai/openspec@latest` fails | Report the exact installation error | No |
| 2 | Installed CLI version conflicts with the existing `config.yaml` schema version | Report the version mismatch. If `config.yaml` does not yet exist, proceed with a fresh `openspec init` and skip this version-conflict check. | No |
| 3 | CLI command is not found, or `openspec context --json` fails to resolve a valid `openspec/` root path | Report the setup requirement | No |
| 4 | A legacy prompt has no corresponding command skill in the table above | Report that no migration path exists | No |
| 5 | A MODIFIED or REMOVED requirement name does not exist in the main spec (see On Archive) | Report the mismatch instead of archiving | No |
| 6 | Any Quality Gate Checklist item is unmet (see below) | Report which items are unmet | No |

If only some legacy prompts lack a migration path, proceed with the ones that do and report only the missing ones.

If `openspec context --json` succeeds but returns an unrecognized schema version,
treat this the same as Stop Condition #2.

## Core Commands

| Command                        | Effect                                                    |
|--------------------------------|-----------------------------------------------------------|
| `/opsx:propose <slug>`         | Create a new change folder with all planning artifacts     |
| `/opsx:explore [topic]`        | Investigate and think through ideas before proposing       |
| `/opsx:apply [slug]`           | Implement tasks from `tasks.md`                           |
| `/opsx:sync [slug]`            | Preview-merge delta specs into main specs                  |
| `/opsx:archive [slug]`         | Merge deltas into specs/ and move change to archive/       |

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
- WHEN  <action>
- THEN  <expected outcome>

## MODIFIED Requirements

### Requirement: <Existing Requirement Name>
<Updated description>
(Previously: <what it said before>)

## REMOVED Requirements

### Requirement: <Name>
(Removed because: <reason>)
```

## On Archive

- The domain name is taken from the delta spec folder path openspec/changes/<slug>/specs/<domain>/spec.md.

## Quality Gate Checklist (before archive)

- [ ] All tasks in `tasks.md` are complete.
- [ ] All new scenarios have passing tests.
- [ ] No removed requirements are still referenced elsewhere.

If any checklist item cannot be verified due to missing data, treat it as unmet and report which items could not be verified.

If any Quality Gate Checklist item is unmet, do not run `/opsx:archive` (see Stop
Conditions #6).
