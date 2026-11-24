# Proposal

## Why

Software Fabric currently defines proposal sections in repository instructions,
templates, persona guidance, and canonical specifications while the installed
OpenSpec schema supplies a different proposal template through the CLI. Agents
must therefore reconcile conflicting formats by inference, which weakens
validation and allows generated proposals to drift as OpenSpec evolves.

## Scope

- Adopt the OpenSpec CLI-provided `Why`, `What Changes`, `Capabilities`, and
  `Impact` structure as the core proposal format.
- Preserve valuable Software Fabric controls for scope boundaries, scenarios,
  acceptance criteria, UX applicability, legal/IP escalation, and Build/Buy/Vibe
  decisions as an explicit extension layer.
- Define one precedence rule: CLI-provided schema instructions define the core;
  repository rules define mandatory extensions and constraints.
- Align proposal templates, canonical requirements, persona guidance, command
  skills, and focused validation with that layered contract.
- Allow a transition for existing active proposals that use compatible legacy
  headings, while generating the new format for all new proposals.

## Out of Scope

- Replacing the OpenSpec CLI, forking its schema, or maintaining a copied package
  template.
- Reformatting archived proposals unless needed as executable migration evidence.
- Changing the purpose of design or delta-spec artifacts.
- Introducing a new approval format or altering implementation and archive
  acceptance gates.
- Requiring Software Fabric-only extensions for unrelated OpenSpec consumers.

## What Changes

- Define a layered Software Fabric proposal contract over the selected OpenSpec
  schema instead of a competing replacement template.
- Require each listed capability to map to an existing or new delta spec so the
  proposal-to-spec relationship remains machine-checkable.
- Retain concise product scenarios and binary acceptance criteria in proposals,
  while keeping detailed normative behavior in delta specs and technical
  decisions in `design.md`.
- Update proposal-generation guidance to use `openspec instructions <artifact>`
  as the source of the core headings and apply local extensions afterward.
- Add compatibility validation for legacy `Intent` and `Affected Domains`
  headings during the transition without generating those headings in new
  proposals.
- Add focused tests for core schema sections, local extension sections, valid
  capability mapping, and legacy compatibility.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `idea-capture`: Define the authoritative layered proposal format, generation
  precedence, capability-to-delta mapping, validation behavior, and bounded
  legacy compatibility.

## UX Applicability

```json
{
  "required": false,
  "reason": "This change affects OpenSpec planning guidance, templates, and validation only; it does not alter a visual interface or user-facing interaction."
}
```

## Build / Buy / Vibe

**Adopt upstream:** use the OpenSpec CLI package as the maintained source for
schema-specific core structure. **Build only:** the Software Fabric extension
contract and focused validation. No purchase or bounded AI-generated product is
needed.

## Legal / IP Notes

No sensitive data, regulated decision-making, proprietary algorithm, or
third-party content is introduced. Existing OpenSpec licensing and attribution
obligations remain unchanged.

## Scenarios

### Scenario: New proposal receives one coherent format

- GIVEN the Product Owner starts a proposal for an initialized OpenSpec project
- WHEN the agent requests CLI instructions for the proposal artifact
- THEN it uses the CLI-provided core sections
- AND appends all mandatory Software Fabric extension sections
- AND does not copy or infer a stale repository-owned replacement for the core
  template

### Scenario: Proposal capabilities produce matching deltas

- GIVEN a proposal lists a new or modified capability
- WHEN the proposal is validated for planning completeness
- THEN a corresponding delta spec exists at the declared capability path
- AND an unrelated, missing, or duplicate capability mapping is reported as a
  validation error

### Scenario: A proposal contains a valuable failure case

- GIVEN a captured idea has user-observable behavior
- WHEN the Product Owner records product scenarios
- THEN the proposal contains at least three concise scenarios
- AND at least one scenario describes an error, rejection, or boundary outcome
- AND detailed normative behavior remains in the affected delta specs

### Scenario: Legacy active proposal remains usable during migration

- GIVEN an active proposal still uses `Intent` instead of `Why` or
  `Affected Domains` instead of `Capabilities`
- WHEN compatibility validation runs during the migration window
- THEN the compatible legacy heading is accepted
- AND the proposal remains subject to all Software Fabric extension requirements
- AND new proposals are still generated using the layered format

### Scenario: Conflicting guidance blocks generation

- GIVEN the repository extension contract conflicts with a selected schema
  instruction in a way that cannot be reconciled without guessing
- WHEN an agent attempts to create the proposal
- THEN generation stops with the conflicting source and required decision
- AND no implementation begins from a partially captured proposal

## Acceptance Criteria

- [ ] New proposals use the selected CLI schema's core headings and mandatory
      Software Fabric extension sections without duplicate replacement
      templates.
- [ ] The precedence rule names the CLI instructions as the authoritative core
      and repository guidance as the extension and policy layer.
- [ ] Every listed capability maps to exactly one corresponding delta spec path.
- [ ] Proposal generation preserves scope, non-goals, product scenarios, binary
      acceptance criteria, UX applicability, legal/IP flags, and Build/Buy/Vibe
      guidance.
- [ ] Focused automated tests cover valid layered proposals, missing required
      sections, capability mapping failures, and bounded legacy compatibility.
- [ ] Product Owner persona guidance, proposal skills, local templates, canonical
      specs, and validation guidance describe the same contract.
- [ ] Existing active proposals remain readable during the migration, while new
      proposals do not generate legacy primary headings.

## Impact

- OpenSpec source specification:
  `openspec/specs/idea-capture/spec.md`.
- Proposal intake template:
  `openspec/templates/idea-to-spec.md`.
- Product Owner and OpenSpec proposal command guidance under `.github/agents/`
  and `.github/skills/`.
- Focused OpenSpec artifact validation and its tests under `.github/scripts/`.
- No runtime application, dependency, API, database, or infrastructure changes.
