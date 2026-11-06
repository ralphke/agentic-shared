# Design

## Context

See `proposal.md` for motivation and
`specs/sdlc-process/spec.md` for the required behavior. The sync code discovers
files under each declared asset root in both the installed and target source
releases. When a shared file disappears upstream, synchronization removes a
consumer copy that still matches the installed source; protected paths are
excluded.

The current prompt wrappers are also named by the policy-restoration script,
strict-policy tests, command-skill tests, README, and OpenSpec workflow
instructions. Removing only the prompt files would leave those paths and
compatibility assertions stale or make restoration fail.

## Goals / Non-Goals

**Goals:**

- Publish OpenSpec command skills, rather than shared prompt wrappers, as the
  shared workflow entry points.
- Let consumers synchronize removal of unchanged shared wrappers.
- Preserve `.github/prompts/local/**` and support consumer manifests that
  declare the `prompts` asset group.
- Remove active documentation and test dependencies on the shared wrappers.

**Non-Goals:**

- Changing command-skill behavior or OpenSpec CLI workflow semantics.
- Deleting consumer-local prompts, consumer overrides, or consumer files.
- Rewriting historical migration artifacts or changing consumer repositories.

## Decisions

### Keep the `prompts` asset group and protected local paths

Keep `prompts` in manifest validation and `ASSET_ROOTS`, and keep the
`.github/prompts/local/**` protection. A consumer that still declares the group
needs the sync engine to compare its installed and target releases so unchanged
shared wrappers can be removed. The protected path prevents consumer-local
files from being considered for shared updates.

Removing the manifest group would reject existing manifests before they can
receive the retirement. Removing its asset root would prevent the sync engine
from finding installed prompt files to delete. Neither is required to stop
publishing shared wrappers.

### Retire wrapper-specific policy restoration and tests

Limit `restore_openspec_contracts.py` targets to the maintained command skills.
Remove tests that require prompt deprecation banners or read deleted prompt
files. Keep the tests that verify command-skill prerequisites and policy
restoration. Add a sync regression test for deletion of an unchanged shared
prompt and preservation of a protected local prompt.

### Update current guidance, not migration history

Remove compatibility-window claims and prompt-to-skill wrapper mappings from
current README, Copilot, and OpenSpec workflow guidance. Leave completed
migration artifacts unchanged: they record the former transition decision and
the separately proposed retirement, rather than current usage guidance.

### Remove only shared prompt wrappers

Delete the 13 root-level `.prompt.md` files. Do not add a placeholder or copy
for `.github/prompts/local/`; that reserved path belongs to consumers and is
preserved through manifest protection and tests.

## Risks / Trade-offs

- **A consumer has edited a formerly shared wrapper** → Existing synchronization
  treats a modified copy as a local override when the upstream file disappears.
  The retirement test guarantees removal only for an unchanged shared copy;
  consumer override handling remains reviewable in the sync pull request.
- **Active instructions still name a prompt wrapper** → Search active
  documentation, scripts, tests, and workflows for wrapper paths and remove
  only references that require the shared wrapper. Historical OpenSpec records
  remain intentionally untouched.
- **The prompts directory becomes empty upstream** → Git does not retain empty
  directories. This is expected; the manifest asset root and consumer-local
  protection continue to work for consumer repositories.

## Migration Plan

1. Remove the shared wrappers and update current guidance and tests in this
   repository.
2. Verify a three-way sync from the installed release to this release removes
   unchanged shared wrappers and preserves protected consumer-local prompts.
3. Distribute the change through the normal tagged release and reviewable
   consumer synchronization pull request. Do not edit consumer repositories
   directly.

## Open Questions

None.
