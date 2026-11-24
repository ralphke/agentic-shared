# Design

## Context

See [proposal.md](./proposal.md) for the motivation. The installed OpenSpec
`spec-driven` schema currently returns the proposal core headings through
`openspec instructions proposal --json`, while repository templates, the
Product Owner persona, `idea-capture`, and validation guidance independently
define a different proposal format. Existing active changes also contain legacy
headings, so a compatibility period is required.

## Goals / Non-Goals

**Goals:**

- Define one precedence rule for proposal generation.
- Preserve Software Fabric's approval and handoff information without copying
  OpenSpec package templates.
- Make capability-to-delta mapping mechanically verifiable.
- Keep active legacy proposals usable without making legacy headings the
  generation default.

**Non-Goals:**

- Reimplement or replace OpenSpec schema behavior.
- Change the meaning or ownership of delta specs, design, or tasks.
- Modify archived changes as a migration activity.
- Add a second artifact-generation mechanism.

## Decisions

### Use CLI instructions as the core template source

Proposal workflows will run `openspec instructions proposal --change <name>
--json`, read `instruction`, `template`, `rules`, and `resolvedOutputPath`, then
write the core from that returned contract.

This avoids maintaining a stale copy of schema-owned headings. The alternative
of updating a checked-in template whenever OpenSpec changes was rejected because
it duplicates package-owned behavior and creates silent version drift.

### Add an explicit Software Fabric extension list

After the schema core, repository guidance will require:

- `Scope`
- `Out of Scope`
- concise `Scenarios`
- `Acceptance Criteria`
- `UX Applicability`
- `Build / Buy / Vibe`
- `Legal / IP Notes` when applicable

`What Changes`, `Capabilities`, and `Impact` replace their overlapping legacy
counterparts: `Approach` moves to design, and `Affected Domains` is represented
by capability mappings. A local guidance file may describe these extensions but
must not restate or embed the CLI-owned core template.

### Validate composition rather than exact whole-file shape

Focused Python validation will inspect proposal sections, Software Fabric
extension requirements, and capability-to-delta correspondence. It will not
compare the entire proposal against one hard-coded markdown template because
custom schemas and future OpenSpec package versions may legitimately change the
core.

The validator may use deterministic heading aliases only during the migration.
It must reject contradictions rather than treating the presence of any alias as
sufficient.

### Enforce capability traceability by relative path

The proposal's `New Capabilities` and `Modified Capabilities` entries will be
parsed as the source of expected delta paths:
`specs/<capability-path>/spec.md`. Validation will require the sets of declared
capabilities and existing delta specs to match exactly. New capability paths
must follow kebab-case path segments, while modified capability paths must
exist under `openspec/specs/`.

### Bound legacy compatibility to recognized aliases

The validator will support only these legacy aliases during migration:

- `Intent` as an alias for the schema core's `Why`
- `Affected Domains` as an alias source when equivalent `Capabilities`
  mapping is present

Aliases do not waive extension checks, scenario checks, UX validation, or
acceptance requirements. New generation guidance must never emit them.

## Risks / Trade-offs

- [Risk] A future schema adds or renames headings, causing assumptions in local
  checks to become stale. → Keep validation focused on repository extensions
  and capability traceability, and derive the core from each CLI instruction
  response.
- [Risk] Legacy compatibility could prevent migration. → Restrict aliases to
  two known headings, cover them with negative tests, and remove them after
  active changes are archived.
- [Risk] Capability parsing could accept malformed paths. → Parse only the
  capability list region and validate exact path normalization, uniqueness, and
  delta correspondence.
- [Risk] Multiple guidance surfaces could drift again. → Make the canonical
  source spec define behavior, let the local template point to CLI composition,
  and add focused regression tests over representative assets.

## Migration Plan

1. Add the layered delta contract and focused validator tests.
2. Update the local proposal template, Product Owner guidance, and OpenSpec
   command skill wording to apply CLI core instructions plus repository
   extensions.
3. Keep `openspec/specs/idea-capture/spec.md` untouched during implementation;
   only the change delta contains the proposed canonical behavior.
4. Keep the two legacy aliases valid for active changes.
5. Run OpenSpec strict validation and focused Python tests.
6. Apply and archive this change only after external quality gates have
   evidence; the gated archive sync is the first operation that updates the
   canonical `idea-capture` specification.
7. After no active proposal uses legacy aliases, create a separate cleanup
   change to remove compatibility. Rollback is to revert the planning guidance
   and validator changes together; no runtime data or deployment migration is
   involved.
