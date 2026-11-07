# Copilot instructions

## Repository snapshot

This repository is a shared library of reusable agentic SDLC assets intended for
synchronization into consumer repositories.

Primary shared artifacts:

- `README.md`
- `.github/ISSUE_TEMPLATE/`
- `.github/agents/`
- `.github/skills/`
- `.github/workflows/`
- `.github/instructions/`
- `.github/copilot-instructions.md`
- `openspec/`

## Purpose

This repository is the canonical home for reusable agentic SDLC assets that are
synchronized into consumer repositories.

It is not a standalone application or workshop runtime. It provides shared
definitions, skills, workflows, and spec templates for other repos to consume.
Fabric workflows are maintained as separately owned `fabric-*` command skills
under `.github/skills/`. Generated `openspec-*` skills remain upstream-owned
and are excluded from shared synchronization; shared prompt wrappers are not
published.

## Current content model

- `.github/ISSUE_TEMPLATE/` — shared issue intake forms
- `.github/agents/` — persona definitions for the Software Fabric flow
- `.github/skills/` — reusable playbooks and OpenSpec command skills
- `.github/prompts/local/` — reserved for consumer-owned prompt extensions
- `.github/workflows/` — shared workflow definitions for consumer repos
- `.github/scripts/` — manifest validation and synchronization tools
- `.github/instructions/` — shared instruction files and policy guidance
- `.github/copilot-instructions.md` — shared Copilot guidance
- `openspec/templates/idea-to-spec.md` — shared OpenSPEC-compatible spec
  template

## Recommended usage

1. Update shared artifacts in this repository.
2. Pin consumer repositories to a tagged release and sync compatible files
   through a reviewable pull request.
3. Put consumer-specific agents, skills, prompts, and instructions under their
   reserved `local/` directories.
4. Keep consumer-specific code, infrastructure, runtime docs, and local specs in
   the consuming repo.

## Shared agent asset standard

Repository-owned files in `.github/agents/` and `.github/skills/` follow this
standard; do not rewrite upstream-generated skill bodies to impose it:

- skill files define a clear purpose, trigger, execution steps, quality checks,
  and expected output
- persona files define role, responsibilities, behavior rules, stage handoff,
  and delivery expectations
- the wording stays action-oriented, scoped, and aligned with the Software
  Fabric flow
- changes remain governance-focused and avoid scope creep into product
  implementation or runtime features

## Shared workflow changes

- For shared workflow changes, check affected skills, personas, instructions,
  README guidance, restoration tooling, and contract tests for consistency.
  Preserve archived history and consumer-local extensions unless explicitly in
  scope.
- Verify CLI syntax against the installed supported version's help. Do not
  assume a chat skill has a one-to-one terminal equivalent. Identify upstream
  OpenSpec behavior separately from Software Fabric policy, and follow the
  accepted ownership plan when changing generated assets.

## Consumer guidance

- Treat this repository as the authoritative source for shared agentic SDLC
  content.
- Use `.agentic-shared.yml` to declare the shared release, asset groups,
  ownership modes, and protected paths.
- Managed synchronization conflicts must be resolved by promoting the change
  upstream or explicitly reviewing the consumer override.
- Existing Fabric consumers default to Fabric. An explicit standalone OpenSpec
  selection routes to unchanged upstream skills without Fabric agent steps.
  Use `route_fabric_workflow.py` to report the action's route. Neither mode nor
  direct CLI use bypasses configured repository merge or release controls.

## Notes

- If a consumer repo adds new tooling, update this file only when the shared
  guidance changes.
- The README is the best source for repository purpose and current contents.
- This repo focuses on shared artifact definitions, not implementation runtime
  tooling.
- Fabric consumers require Node.js 26 or later and OpenSpec 1.16.0; install it
  with `npm install -g @fission-ai/openspec@1.16.0`. This is the Fabric-supported
  baseline, not upstream OpenSpec's runtime requirement. Initialize only with
  explicit authorization, retain existing `openspec/` paths, and verify setup with
  `openspec context --json`.
- Command skills stop without changing artifacts when the OpenSpec CLI is
  unavailable; they do not fall back to prompt wrappers.
