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
- `.github/prompts/` - Copilot prompt files and SDLC entry points
- `.github/instructions/` - shared instruction files
- `.github/copilot-instructions.md` - shared baseline Copilot guidance
- `spec/openspec/templates/spec-template.md` - shared OpenSPEC delta spec template

## Consumption model

Most of these assets are **repository content**, not reusable `workflow_call` modules. That means consumer repositories should **sync** compatible files from this repository instead of editing divergent local copies.

Recommended pattern:

1. Edit shared artifacts here.
2. Sync them into consumer repositories through automation PRs.
3. Keep product-specific code, infrastructure, runtime docs, and local specs in the consuming repo.

## Current consumers

| Repository | Relationship |
| --- | --- |
| `ralphke/Agentic-Coding` | Full Software Fabric consumer; syncs the complete shared agentic SDLC content set |
| `ralphke/Agentic-DevOps` | Selective consumer; keeps Azure, pipeline runtime, and local OpenSpec content in-repo |

## Notes on compatibility

`Agentic-Coding` already matches the shared `spec/openspec/` conventions, so it can consume the full content set directly.

`Agentic-DevOps` currently uses now `spec/openspec/`, so it adopts the shared content as these paths are aligned.

## Update policy

- Treat this repository as the canonical home for shared agentic assets.
- Avoid editing synchronized files directly in consumer repositories unless the change is immediately promoted back here.
