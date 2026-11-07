# Delta for personas

## ADDED Requirements

### Requirement: Upstream OpenSpec Skill Ownership

Upstream `openspec-*` skills MUST remain upstream-owned. Fabric-specific
orchestration MUST use separately named `fabric-*` entry points and MUST
identify differences from upstream workflows.

#### Scenario: Upstream skills are refreshed

- GIVEN a supported OpenSpec upgrade refreshes upstream skills
- WHEN the integration is updated
- THEN Fabric policy is not inserted into upstream-owned skill bodies
- AND separately owned Fabric entry points retain their governance behavior

#### Scenario: Fabric workflow differs from upstream

- GIVEN an upstream action permits behavior disallowed for Fabric-managed work
- WHEN the Fabric entry point handles the action
- THEN it applies the Fabric rule and identifies the distinction
- AND does not describe that rule as an OpenSpec CLI guarantee

### Requirement: Safe Fabric Entry-Point Migration

Consumer migration MUST preserve local extensions and product planning data
and MUST surface ownership conflicts for review before changing those files.

#### Scenario: Consumer migrates customized skills

- GIVEN a consumer has customized an existing shared `openspec-*` skill
- WHEN the consumer adopts the separated entry points
- THEN the migration reports the conflict for explicit review
- AND does not silently overwrite or delete the customization

#### Scenario: Consumer retains product planning data

- GIVEN a consumer has local extensions and active OpenSpec changes
- WHEN shared Fabric assets are synchronized
- THEN protected local extensions and active changes remain unchanged
- AND the migration guidance identifies replacement Fabric invocations
