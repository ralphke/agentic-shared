# Copilot instructions

## Repository snapshot

This repository is a shared library of reusable agentic SDLC assets intended for synchronization into consumer repositories.

Primary shared artifacts:

- `README.md`
- `.github/ISSUE_TEMPLATE/`
- `.github/agents/`
- `.github/skills/`
- `.github/prompts/`
- `.github/workflows/`
- `.github/instructions/`
- `.github/copilot-instructions.md`
- `specs/openspec/`

## Purpose

This repository is the canonical home for reusable agentic SDLC assets that are synchronized into consumer repositories.

It is not a standalone application or workshop runtime. It provides shared definitions, prompts, workflows, and spec templates for other repos to consume.

## Current content model

- `.github/ISSUE_TEMPLATE/` — shared issue intake forms
- `.github/agents/` — persona definitions for the Software Fabric flow
- `.github/skills/` — reusable playbooks for agent personas
- `.github/prompts/` — Copilot entry points and prompt templates
- `.github/workflows/` — shared workflow definitions for consumer repos
- `.github/scripts/` — manifest validation and synchronization tools
- `.github/instructions/` — shared instruction files and policy guidance
- `.github/copilot-instructions.md` — shared Copilot guidance
- `spec/openspec/templates/idea-to-spec.md` — shared OpenSPEC-compatible spec template

## Recommended usage

1. Update shared artifacts in this repository.
2. Pin consumer repositories to a tagged release and sync compatible files through a reviewable pull request.
3. Put consumer-specific agents, skills, prompts, and instructions under their reserved `local/` directories.
4. Keep consumer-specific code, infrastructure, runtime docs, and local specs in the consuming repo.

## Consumer guidance

- Treat this repository as the authoritative source for shared agentic SDLC content.
- Use `.agentic-shared.yml` to declare the shared release, asset groups, ownership modes, and protected paths.
- Managed synchronization conflicts must be resolved by promoting the change upstream or explicitly reviewing the consumer override.

## Notes

- If a consumer repo adds new tooling, update this file only when the shared guidance changes.
- The README is the best source for repository purpose and current contents.
- This repo focuses on shared artifact definitions, not implementation runtime tooling.
