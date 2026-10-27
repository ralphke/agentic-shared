# Proposal

## Why

The Operations SRE Agent's related skills are discoverable in the shared skills
directory, but their intended ownership and usage are not declared in the agent
instructions. An explicit mapping will make it clear which operational tasks
should use each skill without implying runtime-enforced exclusivity.

## What Changes

- Add an **Associated Skills** section to the Operations SRE Agent definition.
- Associate `workflow-retrospective` with recurring SDLC process reviews and
  improvement requests.
- Associate `openspec-archive-change` with archiving only after the agent's
  operational stability and quality gates pass.
- State that the mapping guides intended skill use; it does not restrict other
  agents or change skill discovery behavior.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `personas`: Specify explicit, task-oriented skill associations in the
  Operations SRE Agent instructions.

## Impact

- Affected domain: personas.
- Affected shared asset: `.github/agents/operations-sre.agent.md`.
- No skill files, runtime configuration, synchronization behavior, or other
  agent definitions change.

## Scope and Non-Goals

- Scope is limited to the Operations SRE Agent and its two directly relevant
  skills.
- This change documents intended agent-to-skill associations; it does not add a
  runtime router, access control, or machine-enforced skill binding.
- Other agents' skill mappings are out of scope.

## Acceptance Criteria

- The Operations SRE Agent explicitly names both associated skills and the
  situations in which each should be used.
- The archive skill association is conditioned on the agent's existing
  operational gates.
- The retrospective skill association does not broaden the agent's
  responsibilities to feature implementation or incident response.
- The instructions do not claim that skills are exclusive to the Operations SRE
  Agent or that the mapping is enforced by the runtime.

## Scenarios

### Choosing the retrospective skill

- GIVEN the Operations SRE Agent is asked to investigate recurring SDLC friction
- WHEN it selects a skill for the work
- THEN it identifies `workflow-retrospective` as the relevant skill.

### Choosing the archive skill

- GIVEN the Operations SRE Agent has confirmed the operational archive gates are
  satisfied
- WHEN it is ready to archive the change
- THEN it identifies `openspec-archive-change` as the relevant skill.

### No runtime exclusivity

- GIVEN another agent or user invokes a skill outside this mapping
- WHEN the runtime discovers or runs that skill
- THEN this mapping does not claim to prevent that use.
