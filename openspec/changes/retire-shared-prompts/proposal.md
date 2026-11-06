# Proposal: Retire Shared OpenSpec Prompt Wrappers

## Why

The shared prompt wrappers duplicate workflow entry points now maintained as
OpenSpec command skills. Because new shared workflow work must use the OpenSpec
CLI-backed skills, continuing to publish the wrappers creates stale guidance
and unnecessary entry-point ambiguity.

## What Changes

- **BREAKING:** Remove the 13 shared `.prompt.md` wrappers from
  `.github/prompts/`.
- Retain the corresponding maintained skills under `.github/skills/` as the
  shared workflow entry points; their OpenSpec CLI prerequisites and stop
  behavior remain mandatory.
- Remove current documentation, tests, and policy mappings that describe the
  shared wrappers or their compatibility window. Keep historical OpenSpec
  change records intact.
- Preserve consumer-owned prompt files under `.github/prompts/local/**` and
  keep the `prompts` manifest group and protected-path handling so consumers
  can synchronize removal of old shared wrappers without losing local files.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `sdlc-process`: Make maintained OpenSpec command skills the only shared
  workflow entry points while allowing consumer-local prompt files.

## Scope

- The 13 wrappers are `opsx-apply`, `opsx-archive`, `opsx-bulk-archive`,
  `opsx-continue`, `opsx-explore`, `opsx-ff`, `opsx-new`, `opsx-onboard`,
  `opsx-propose`, `opsx-sync`, `opsx-update`, `opsx-verify`, and
  `sdlc-kickoff`.
- Update the repository README, shared Copilot guidance, OpenSpec workflow
  instructions, sync-related tests, and any implementation references that
  require the shared wrappers.
- Verify that synchronization removes unchanged retired shared wrappers while
  preserving `.github/prompts/local/**`.

## Non-Goals

- Deleting or rewriting consumer-owned prompt files or consumer repositories.
- Removing support for consumer-local prompts or the `prompts` manifest asset
  group.
- Reworking the maintained skill implementations or removing OpenSpec CLI
  command behavior.
- Editing historical proposal, design, or task artifacts to erase the
  compatibility decision made by the migration change.

## Scenarios

### Scenario: New shared workflows use maintained command skills

- GIVEN a consumer adopts the updated shared assets
- WHEN it selects a shared Software Fabric workflow
- THEN the maintained command skill is the shared entry point
- AND the skill requires the OpenSpec CLI and does not fall back to a prompt
  wrapper

### Scenario: Sync retires shared wrappers without losing local prompts

- GIVEN a consumer has an unchanged copy of a shared prompt wrapper and a
  consumer-owned prompt under `.github/prompts/local/`
- WHEN the consumer synchronizes the release that retires shared wrappers
- THEN the unchanged shared wrapper is removed
- AND the consumer-owned local prompt remains untouched

### Scenario: Shared assets no longer advertise a compatibility window

- GIVEN repository documentation and tests describe the supported shared
  workflow entry points
- WHEN the retirement change is complete
- THEN they identify the maintained OpenSpec command skills as the shared
  entry points
- AND they no longer require or promise compatibility for shared prompt
  wrappers

## Acceptance Criteria

- [ ] All 13 shared prompt wrappers are removed; the maintained counterpart
      skills remain available.
- [ ] Current documentation, tests, and policy references no longer describe
      shared prompt wrappers as supported or require their compatibility
      banners.
- [ ] The `prompts` manifest group and `.github/prompts/local/**` protection
      remain supported for consumer-owned prompt assets.
- [ ] A focused synchronization test proves an unchanged retired shared prompt
      is removed while a protected local prompt is preserved.
- [ ] The `sdlc-process` delta records the skills-only shared entry-point
      contract and the local-prompt exception.
- [ ] OpenSpec validation and the relevant focused tests pass.

## Affected Domains

- `sdlc-process`

## UX Applicability

```json
{"required": false, "reason": "This repository-content and synchronization change affects no visual interface."}
```

## Impact

- `.github/prompts/`, `.github/skills/`, README and shared instructions
- `.github/scripts/` synchronization behavior and tests
- `openspec/specs/sdlc-process/` through a reviewed delta
- Consumer synchronization of the `prompts` asset group
