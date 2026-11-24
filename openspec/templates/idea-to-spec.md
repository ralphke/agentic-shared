# Software Fabric Proposal Composition

Use this guide to extend, not replace, the proposal format supplied by the
selected OpenSpec schema.

## Before Capture

1. Assess the idea outside the worktree and clarify material ambiguity with no
   more than three focused questions.
2. Offer **Proceed**, **Defer**, or **Do not pursue**.
3. Write nothing until the requester explicitly chooses Proceed or asks to
   create the named planning artifacts. Capture authorization is not proposal
   or implementation approval.

## Core Structure Source

After Proceed:

1. Scaffold with `openspec new change "<slug>"`.
2. Run `openspec instructions proposal --change "<slug>" --json`.
3. Use the returned `template`, `instruction`, `rules`, `dependencies`, and
   `resolvedOutputPath` as the authoritative source for the schema-owned core.
4. Do not copy a previously captured proposal or an OpenSpec package template
   into this file or another repository template, and do not emit legacy
   `Intent` or `Affected Domains` headings for new proposals.

For the current `spec-driven` schema, the core includes the change motivation,
the list of changes, capability declarations, and impact. Obtain the exact
headings from the CLI rather than inferring or hard-coding them.

If repository policy cannot be composed with the returned schema without
choosing between conflicting behaviors, stop and report both sources.

## Required Software Fabric Extensions

Append these extension sections when they are not already represented by the
selected schema:

### Scope

List concrete outcomes and deliverables included in the change. Keep this
implementation-agnostic.

### Out of Scope

List exclusions and non-goals that bound the approval and prevent accidental
scope expansion.

### Scenarios

Provide at least three concise Given/When/Then product scenarios, including at
least one unhappy, rejection, or boundary case. Keep detailed normative
requirements and their scenarios in the delta specs.

### Acceptance Criteria

Provide at least three binary checkboxes. Each criterion must be independently
verifiable by a person or automated check.

### UX Applicability

Include exactly one fenced JSON object with a boolean `required` and a nonempty
scope-backed `reason`. Set `required` to `true` only when the accepted scope
affects a visual interface.

### Build / Buy / Vibe

State whether the outcome is best built in-house, purchased or adopted, or
implemented as a bounded AI-generated internal tool.

### Legal / IP Notes

Identify applicable proprietary-content, licensing, regulated-data,
intellectual-property, financial, medical, privacy, or third-party risks. If no
trigger applies, record that the bounded scope has no legal/IP escalation.

## Capability Mapping

Use the schema's new- and modified-capability structure:

- Each new capability becomes
  `specs/<new-capability-path>/spec.md`.
- Each modified capability uses the exact existing path under `openspec/specs/`
  and creates the matching change delta.
- Every declared capability and every delta path must correspond one-to-one.
- Do not invent a capability merely to satisfy validation.

## Validation and Handoff

Before requesting proposal acceptance, verify:

- The selected schema core is complete.
- Every required extension is present and substantive.
- Scope exclusions are nonempty.
- At least three scenarios and three acceptance criteria exist.
- At least one proposal scenario covers failure or a boundary.
- Capability declarations match delta spec paths exactly.
- UX applicability is unique and valid.

Explicit acceptance of the proposal is still separate from capture. Acceptance
of the current proposal and delta specs is required before implementation.
