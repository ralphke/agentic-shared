---
applyTo: "spec/openspec/**"
---

# OpenSpec Workflow Instructions

When working with files in `spec/openspec/`, always follow the OpenSpec
workflow (https://github.com/Fission-AI/OpenSpec).

## Command Skills

Use the shared OpenSpec command skills for new workflows. They require Node.js 26 or
later and a working OpenSpec CLI. Before use, install and initialize the CLI:

```powershell
npm install -g @fission-ai/openspec@latest
openspec init
openspec context --json
```

Retain the repository's `spec/openspec/` configuration during initialization. If the CLI
or root resolution is unavailable, stop without modifying artifacts and report the setup
requirement; do not fall back to a deprecated prompt wrapper.

| Legacy prompt | Command skill |
|---|---|
| `opsx-propose.prompt.md` | `openspec-propose` |
| `opsx-apply.prompt.md` | `openspec-apply-change` |
| `opsx-verify.prompt.md` | `openspec-verify-change` |
| `sdlc-kickoff.prompt.md` | `software-fabric-kickoff` |

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
- MODIFIED sections → replace existing requirement in main spec
- REMOVED sections → deleted from main spec
- Change folder → moved to `spec/openspec/changes/archive/`

## Quality Gate Checklist (before archive)

- [ ] All CI checks green
- [ ] Security scan: no HIGH/CRITICAL findings
- [ ] Code coverage ≥ 80%
- [ ] At least one review approval
- [ ] All acceptance criteria checked off in proposal.md
