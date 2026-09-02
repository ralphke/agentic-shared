---
applyTo: "spec/openspec/**"
---

# OpenSpec Workflow Instructions

When working with files in `spec/openspec/`, always follow the OpenSpec
workflow (https://github.com/Fission-AI/OpenSpec).

## Command Skills

Use the shared OpenSpec command skills for new workflows. Core Commands (/opsx:*) are
the legacy interface; use Command Skills for all new workflows and only use Core
Commands when explicitly requested. They require Node.js 26 or later and a working
OpenSpec CLI. Before use, install and initialize the CLI:

```powershell
npm install -g @fission-ai/openspec@latest
openspec init
openspec context --json
```

If installation fails, report the exact error and do not proceed with any OpenSpec
workflow commands.

Retain the repository's `spec/openspec/` configuration during initialization. If the
installed CLI version conflicts with the existing `config.yaml` schema version, stop
and report the version mismatch. If the CLI command is not found, or if `openspec
context --json` fails to resolve a valid
`spec/openspec/` root path, stop without modifying artifacts and report the setup
requirement; do not fall back to a deprecated prompt wrapper.

| Legacy prompt | Command skill |
|---|---|
| `opsx-propose.prompt.md` | `openspec-propose` |
| `opsx-apply.prompt.md` | `openspec-apply-change` |
| `opsx-verify.prompt.md` | `openspec-verify-change` |
| `sdlc-kickoff.prompt.md` | `software-fabric-kickoff` |

If a legacy prompt has no corresponding command skill in this table, stop and report
that no migration path exists.

## Core Commands

| Command                        | Effect                                                    |
|--------------------------------|-----------------------------------------------------------|
| `/opsx:propose <slug>`         | Create a new change folder with all planning artifacts     |
| `/opsx:explore [topic]`        | Investigate and think through ideas before proposing       |
| `/opsx:apply [slug]`           | Implement tasks from `tasks.md`                           |
| `/opsx:sync [slug]`            | Preview-merge delta specs into main specs                  |
| `/opsx:archive [slug]`         | Merge deltas into specs/ and move change to archive/       |

## File Locations

- **Source of truth specs:** `spec/openspec/specs/<domain>/spec.md`
- **In-flight changes:** `spec/openspec/changes/<slug>/`
- **Archived changes:** `spec/openspec/changes/archive/<date>-<slug>/`
- **Config:** `spec/openspec/config.yaml`

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

- ADDED sections → appended to main spec
- If a domain referenced in the delta spec has no existing specs/<domain>/spec.md, create the file before appending ADDED sections.
- MODIFIED sections → replace existing requirement in main spec
- If a MODIFIED or REMOVED requirement name does not exist in the main spec, stop and report the mismatch instead of archiving.
- REMOVED sections → deleted from main spec
- Change folder → moved to `spec/openspec/changes/archive/`

## Quality Gate Checklist (before archive)

- [ ] All CI checks green
- [ ] Security scan: no HIGH/CRITICAL findings
- [ ] Code coverage ≥ 80%
- [ ] At least one review approval
- [ ] All acceptance criteria checked off in proposal.md

If any Quality Gate Checklist item is unmet, do not run `/opsx:archive`; report which
items are unmet and stop.
