# Proposal: Separate Software Fabric from OpenSpec

## Why

Software Fabric adds lifecycle governance to OpenSpec, but shared `openspec-*`
skills currently mix upstream workflow behavior with Fabric-specific policies.
This obscures which rules OpenSpec provides, makes upgrades fragile, and can
overstate what the OpenSpec CLI enforces.

Maintainers and consumers need a clear boundary so they can use OpenSpec's
change-management features independently while applying Fabric governance
explicitly to Fabric-managed work.

## Intent

Separate OpenSpec's specification and change mechanisms from Software Fabric's
orchestration and quality policies. Preserve the existing Fabric gates while
making ownership, enforcement, consumer data boundaries, and compatibility
clear and verifiable.

## What Changes

1. **Separate skill ownership.** Keep upstream `openspec-*` skills
   upstream-owned and place Fabric orchestration in separately named `fabric-*`
   skills and instructions. Where an upstream workflow cannot satisfy a Fabric
   requirement, the Fabric integration explicitly owns that difference.
2. **Name the policy boundary.** Explain what OpenSpec allows and what Fabric
   additionally requires for planning, approval, sync, and archive. Preserve
   lightweight OpenSpec use outside Fabric-managed work.
3. **Separate guidance from enforcement.** Identify which rules are agent
   guidance and which are enforced by configured CI and branch protection.
   Enforce mandatory merge and release conditions through those controls where
   applicable, and document what each check verifies and cannot verify.
4. **Preserve the store boundary.** Distribute Fabric assets separately from
   consumer-owned product specifications and changes. Retain the recommended
   consumer-local OpenSpec store and explicit shared-store selection.
5. **Version the integration.** Declare and test explicitly supported OpenSpec
   versions rather than relying solely on `@latest`; review upstream skill
   changes before adoption. Distinguish the Fabric-supported runtime baseline
   from OpenSpec's own requirements.

**BREAKING:** Separating Fabric entry points from locally customized
`openspec-*` skills may require consumers to migrate their invocations and
synchronized assets. Provide a reviewed migration path rather than silently
replacing or deleting consumer-owned content.

## Scope

- The five improvements above, including the shared assets, documentation,
  compatibility checks, and consumer migration needed to deliver them.
- Existing Fabric planning, testing, security, legal, review, and operational
  gates remain in force for Fabric-managed work.
- Document terminal CLI commands separately from agent chat workflows and
  identify direct CLI paths that do not enforce Fabric policy.

## Out of Scope

- Forking or changing the upstream OpenSpec CLI or imposing Fabric rules on
  OpenSpec itself.
- Weakening existing mandatory Fabric gates or claiming that agent instructions
  alone enforce them.
- Moving consumer product specifications or changes into the shared store.
- Modifying consumer repositories or their live branch-protection settings
  directly as part of this proposal.
- New SDLC stages, unrelated persona changes, or product runtime features.

## Approach

Treat OpenSpec as the upstream mechanism and Software Fabric as an explicit
integration and governance layer. Define the handoff and supported versions,
retain consumer ownership boundaries, and make the enforcement evidence and
its limits visible. The accepted design will determine the migration and
implementation details.

## UX Applicability

```json
{
  "required": false,
  "reason": "The change affects agent workflows, repository policy, CI and documentation, not a visual interface."
}
```

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `sdlc-process`: Distinguish OpenSpec mechanics from Fabric policy and
  describe the enforceable and advisory boundaries for Fabric-managed work.
- `personas`: Separate upstream OpenSpec skill ownership from Fabric
  orchestration and its handoffs.
- `testing-standards`: Verify supported integration versions and the behavior
  and limits of applicable automated governance checks.

## Scenarios

### Fabric workflow retains its governance

- GIVEN a change is being managed through Software Fabric
- WHEN a user starts planning, implementation, sync, or archive
- THEN the Fabric integration applies the applicable existing policy gates
- AND identifies those requirements as Fabric policy, not OpenSpec defaults

### Upstream workflow remains independent

- GIVEN a user is using OpenSpec outside Fabric-managed work
- WHEN the user invokes an upstream OpenSpec workflow
- THEN Fabric orchestration is not implicitly presented as an OpenSpec rule
- AND upstream-owned skills are not overwritten with Fabric policy

### Missing enforcement evidence does not become approval

- GIVEN a Fabric-managed change lacks evidence for an applicable mandatory gate
- WHEN the relevant merge or release control evaluates the change
- THEN it blocks progression and identifies the missing evidence
- AND documentation does not claim that a direct CLI command enforces the gate

### Consumer store remains local

- GIVEN a consumer synchronizes Fabric assets using the recommended manifest
- WHEN the consumer creates a product change
- THEN the consumer's local OpenSpec store owns its specifications and change
- AND the shared store is used only when explicitly selected

### Unsupported upstream version is visible

- GIVEN an OpenSpec version outside the declared supported integration range
- WHEN compatibility is checked
- THEN the result reports the unsupported version
- AND it does not claim the integration has passed compatibility checks

## Acceptance Criteria

- [ ] Upstream `openspec-*` skill content is upstream-owned, and Fabric
      orchestration uses separately named `fabric-*` entry points with an
      explicit migration path for existing consumers.
- [ ] Guidance distinguishes OpenSpec behavior from additional Fabric
      requirements for planning, approval, sync, and archive, including chat
      workflows versus terminal CLI commands.
- [ ] Fabric-managed work retains its existing applicable mandatory gates;
      documented merge and release checks identify their evidence, enforcement
      point, and limitations, and block when required evidence is absent.
- [ ] Documentation explicitly states that a direct OpenSpec CLI invocation
      does not itself enforce the Fabric checklist.
- [ ] The recommended consumer manifest keeps product specs local and protects
      active changes; shared-store use remains explicit.
- [ ] The integration declares supported OpenSpec versions and verifies them
      in compatibility tests, including an unsupported-version outcome;
      upgrade guidance requires review of upstream skill changes.
- [ ] Documentation distinguishes Fabric's supported runtime baseline from
      upstream OpenSpec's requirements.
- [ ] Representative affected skills and instructions are assessed before and
      after the change using the same rubric for clarity, structure, execution
      guidance, and handoff quality; results and differences are recorded.

## Affected Domains

- `sdlc-process`
- `personas`
- `testing-standards`

## Build/Buy/Vibe Flag

**Adopt:** use upstream OpenSpec for change mechanics. **Build:** maintain only
the bounded Fabric integration, governance checks, and compatibility tests.

## Legal/IP Notes

The change does not introduce sensitive data or a new external service.
Preserve applicable upstream license and attribution obligations for any
redistributed OpenSpec materials. Escalate if implementation introduces unclear
third-party use rights or another legal-risk trigger.

## Impact

Affects shared skills, instructions, synchronization and migration guidance,
CI governance and compatibility tests, and consumer documentation. Consumer
administrators remain responsible for configuring required branch-protection
checks; local agent guidance cannot enforce restrictions on direct CLI use.
