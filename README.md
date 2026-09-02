# Agentic-shared

Shared reusable agentic SDLC assets for Ralph's repositories.

## Purpose

This repository is the **single source of truth** for the reusable agentic artifacts that were previously split across project repositories.

It currently centralizes:

- GitHub issue templates
- Agent persona definitions
- Skill playbooks
- Copilot prompts and instructions
- Event-driven GitHub workflow definitions
- Agent-ready spec templates
- Workflow retrospective automation for continuous process improvement

## Repository layout

- `.github/workflows/` - canonical workflow definitions intended to be synchronized into consumer repos
- `.github/ISSUE_TEMPLATE/` - shared issue intake forms
- `.github/agents/` - persona definitions used by the Software Fabric flow
- `.github/skills/` - reusable task playbooks for those personas
- `.github/prompts/` - deprecated Copilot prompt wrappers retained for one compatibility release
- `.github/instructions/` - shared instruction files
- `.github/copilot-instructions.md` - shared baseline Copilot guidance
- `.github/scripts/` - manifest validation and consumer synchronization tools
- `openspec/templates/spec-template.md` - shared OpenSPEC delta spec template

## Consumption model

Most of these assets are **repository content**, not reusable `workflow_call` modules. That means consumer repositories should **sync** compatible files from this repository instead of editing divergent local copies.

Recommended pattern:

1. Edit shared artifacts here.
2. Sync them into consumer repositories through automation PRs.
3. Keep product-specific code, infrastructure, runtime docs, and local specs in the consuming repo.

## Consumer manifest

Consumer repositories should copy `.agentic-shared.example.yml` to
`.agentic-shared.yml` and pin a tagged release. The manifest declares which
asset groups are shared and whether each group is `managed`, `extended`, or
`local`.

Validate a manifest before opening a synchronization PR from the repository root:

```bash
python .github/scripts/validate_agentic_shared_manifest.py .agentic-shared.yml
```

Copy `.github/workflows/agentic-shared-sync.yml` into the consumer repository.
Run it manually with a tagged `target_version`. It checks out the installed and
target releases, performs a three-way update, and opens a pull request. A
managed-path conflict fails the workflow before any consumer file is changed.

Use reserved `local/` directories for consumer-only extensions:

- `.github/agents/local/`
- `.github/skills/local/`
- `.github/prompts/local/`
- `.github/instructions/local/`

Consumer changes to shared behavior should be proposed here through an issue
or OpenSpec change. Consumer-specific behavior belongs in a local extension
path and must not edit synchronized files in place.

## OpenSpec command skills

The shared OpenSpec entry points are skills, not prompt files. Consumers that use the
command skills require Node.js 26 or later and the OpenSpec CLI:

```powershell
npm install -g @fission-ai/openspec@latest
openspec init
openspec context --json
```

Run `openspec init` in the consumer repository and retain its existing `openspec/`
configuration. `openspec context --json` must resolve the repository's OpenSpec root
before a command skill can create or modify artifacts.

| Deprecated prompt | Replacement skill |
| --- | --- |
| `opsx-propose.prompt.md` | `openspec-propose` |
| `opsx-apply.prompt.md` | `openspec-apply-change` |
| `opsx-verify.prompt.md` | `openspec-verify-change` |
| `sdlc-kickoff.prompt.md` | `software-fabric-kickoff` |

Shared prompt wrappers remain available for the release that introduces their replacement
skills. A subsequent, separately reviewed breaking release may remove only shared prompt
wrappers after consumer adoption is confirmed. Consumer-owned `.github/prompts/local/`
files remain outside this retirement path.

## Current consumers

| Repository | Relationship |
| --- | --- |
| `ralphke/Agentic-Coding` | Full Software Fabric consumer; syncs the complete shared agentic SDLC content set |
| `ralphke/Agentic-DevOps` | Selective consumer; keeps Azure, pipeline runtime, and local OpenSpec content in-repo |

## Notes on compatibility

`Agentic-Coding` already matches the shared `openspec/` conventions, so it can consume the full content set directly.

`Agentic-DevOps` currently uses `openspec/`, so it adopts the shared content as those paths are aligned.

## Update policy

- Treat this repository as the canonical home for shared agentic assets.
- Pin consumers to tagged releases rather than a moving branch.
- Deliver updates through consumer pull requests so local CI and human review run before merge.
- Managed-path conflicts must fail closed; never overwrite consumer changes automatically.
- Avoid editing synchronized files directly in consumer repositories unless the change is immediately promoted back here.
