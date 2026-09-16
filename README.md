# Agentic-shared

Shared reusable agentic SDLC assets for Ralph's repositories.

## Purpose

This repository is the **single source of truth** for the reusable agentic artifacts that were previously split across project repositories. It is also a standalone OpenSpec root.

OpenSpec is the underlying change-management mechanism for the shared command
skills: it resolves specifications, in-flight changes, planning artifacts,
validation, and archival through the OpenSpec CLI. A clone of this repository
can be registered as a machine-local OpenSpec store when shared specifications
need to be operated on explicitly.

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
- `.github/instructions/` - shared instruction files
- `.github/copilot-instructions.md` - shared baseline Copilot guidance
- `.github/scripts/` - manifest validation and consumer synchronization tools
- `openspec/` - standalone OpenSpec content: configuration, source specifications,
  in-flight changes, and shared templates

## Consumption model

Most of these assets are **repository content**, not reusable `workflow_call` modules.
Consumer repositories should **sync** compatible shared files from this repository
instead of editing divergent local copies. Asset synchronization and OpenSpec store
selection are complementary mechanisms:

- **Synchronization** distributes shared agents, skills, instructions, workflows,
  issue templates, and optional specification content through a reviewed pull request.
- **A consumer OpenSpec store** owns that consumer's product specifications and active
  changes. Command skills use the nearest local `openspec/` root by default.
- **The shared OpenSpec store** owns this repository's shared specifications and changes.
  Consumer feature work must not be created in the shared store.

Recommended pattern:

1. Edit shared artifacts here.
2. Sync them into consumer repositories through automation PRs.
3. Keep product-specific code, infrastructure, runtime docs, source specifications, and
   active OpenSpec changes in the consuming repo.

## Consumer manifest

Consumer repositories should copy `.agentic-shared.example.yml` to
`.agentic-shared.yml` and pin a tagged release. The manifest declares which
asset groups are shared and whether each group is `managed`, `extended`, or
`local`.

The supplied example sets `assets.specs: local` and protects `openspec/changes/**`.
This is the recommended consumer configuration: consumers keep their OpenSpec store
local while receiving the shared command skills and SDLC policy assets. Set
`assets.specs` to `managed` or `extended` only when deliberately adopting shared
`openspec/` content and reviewing the resulting configuration and spec updates.

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

The shared OpenSpec entry points are skills. The command skills use the OpenSpec CLI as
their source of truth for artifact paths, workflow state, and instructions.

### Consumer-local store (recommended)

Consumers that use the command skills require Node.js 26 or later and the OpenSpec CLI.
Initialize or retain an `openspec/` root in the consumer repository:

```powershell
npm install -g @fission-ai/openspec@latest
openspec init
openspec context --json
openspec doctor
```

Run `openspec init` in the consumer repository and retain its existing `openspec/`
configuration. `openspec context --json` must resolve the repository's OpenSpec root
before a command skill can create or modify artifacts. The skills then use that nearest
local root, so consumer proposals, delta specs, and changes remain consumer-owned.

### Shared store (explicit selection)

OpenSpec stores are standalone OpenSpec repositories registered on a developer machine;
they are not a replacement for the synchronization workflow. To inspect the shared store
from a local clone, register it and select it explicitly:

```powershell
openspec store register <path-to-agentic-shared> --id agentic-shared --yes
openspec store list --json
openspec context --json --store agentic-shared
```

After selecting a store, pass `--store agentic-shared` to subsequent OpenSpec commands
that read or modify specs and changes, for example:

```powershell
openspec list --json --store agentic-shared
openspec validate --all --json --store agentic-shared
```

Use the shared store to inspect or maintain shared SDLC content in this repository. Use
a consumer-local store for consumer product work; do not create, apply, or archive
consumer changes in the shared store.

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
