---
applyTo: "openspec/**"
---

# OpenSpec mechanics and work-mode selection

OpenSpec owns the CLI, schemas, artifact graph, resolved roots, and generated
`openspec-*` skills. Do not insert Software Fabric policy into those skills.
Use the installed supported version's help to verify command syntax; a chat
skill invocation is not necessarily a terminal command.

## Select the workflow

Existing Fabric consumers default to Fabric for the current work. Route actions
to the corresponding `fabric-*` skill using
`python .github/skills/fabric-propose/scripts/route_fabric_workflow.py --action <action>`.
An explicit standalone OpenSpec selection uses `--mode standalone` and the
upstream skill unchanged. Do not infer standalone selection merely from an
`openspec-*` command name, nor silently switch modes during handoff.

The planning acceptance, intake, quality, and archive requirements in
`fabric-workflow.instructions.md` apply only to Fabric-managed work. They are
additional Fabric policy, not upstream defaults. In standalone mode do not
apply those agent orchestration steps. Repository-level merge and release
controls remain unchanged in either mode. Direct local CLI operations do not
enforce the Fabric checklist.

## Resolve paths and commands

- Run `openspec --version` and `openspec context --json` before artifact work.
  Report failures; never create or initialize a root implicitly.
- Use returned `planningHome`, `changeRoot`, `artifactPaths`, `contextFiles`,
  and `actionContext` rather than assuming a schema or stale paths.
- Consumer product changes use the nearest local `openspec/` root by default.
  Select the shared store only explicitly. Discover registered store IDs with
  `openspec store list --json`, then retain `--store <id>` on every applicable
  command. Do not move consumer product planning into this shared repository.
- Read status and artifact instructions from the selected root before writing.
  Preserve CLI-controlled blocked states, artifact rules, and edit constraints.
- Check structured validation with `openspec validate <name> --strict --json`.
  Upstream validation is not evidence of Fabric acceptance or lifecycle gates.

## Artifact conventions

The repository uses `openspec/specs/<domain>/spec.md` for source specs and
`openspec/changes/<slug>/` for active changes. Resolve paths through the CLI
when a selected store or custom schema changes them.

Delta files use `# Delta for <domain>`, `## ADDED Requirements`,
`## MODIFIED Requirements`, `## REMOVED Requirements`, and, when applicable,
`## RENAMED Requirements`. Requirements use `### Requirement:` and scenarios
use `#### Scenario:` with Given/When/Then conditions. MODIFIED requirements
preserve existing scenarios unless the accepted change explicitly changes them.
