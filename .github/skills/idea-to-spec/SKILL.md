---
name: idea-to-spec
description:
  Turn an ambiguous idea into an actionable OpenSpec proposal with scope,
  scenarios, and acceptance criteria. Use for idea intake and proposal creation.
  Do not use for design or task implementation or code delivery.
---

# Skill: Idea to OpenSPEC Proposal

**Persona:** Product Owner Agent **Input:** Raw idea text (natural language)
**Output:** An intake decision, or `openspec/changes/<slug>/proposal.md` after
explicit Proceed.

---

## When to Use This Skill

Use this skill when a user submits:

- A GitHub Issue with label `idea`
- A `/fabric-propose <description>` command
- A raw idea in chat that needs structuring

---

## Execution Steps

1. **Parse the idea** — Extract: problem statement, proposed solution, target
   users
2. **Generate slug** — Convert title to kebab-case (e.g., "add csv export" →
   `add-csv-export`)
3. **Validate slug** — Ensure kebab-case, 3–50 chars, starts with letter
4. **Load template and assess** — Read `openspec/templates/idea-to-spec.md`;
   clarify material ambiguity before any capture, asking ≤ 3 focused questions.
   Keep the idea and draft proposal in conversation or session storage.
5. **Pre-Capture Intake Decision** — Follow
   `.github/instructions/fabric-workflow.instructions.md`. Offer Proceed,
   Defer, or Do not pursue. Missing input pauses capture. Defer or rejection
   means no repository writes, sync, archive, task completion, or deletion of
   existing work. A request to create named repository artifacts counts as
   Proceed; do not repeat the decision at handoff. An issue, priority, or raw
   idea alone does not. Proceed is not proposal/spec acceptance or permission
   to implement.
6. **Capture after Proceed** — Use the `fabric-propose` compatibility and
   selected-root checks and the schema paths to scaffold with
   `openspec new change "<slug>"` and obtain proposal instructions. Preserve
   any selected store flag. Never hand-create a change directory or initialize
   implicitly. Capture only the proposal within this skill's scope.
7. **Write proposal.md** — Only after Proceed, fill in all required sections:
   - `## Intent` — 1-2 paragraphs explaining why (what users need, not how to
     build it)
   - `## Scope` — bullet list of inclusions
   - `## Out of Scope` — bullet list of exclusions
   - `## Approach` — high-level strategy (outcomes, not implementation details)
   - `## Build/Buy/Vibe Flag` — note if problem may be better served by existing
     SaaS (Buy) or a bounded AI-generated internal tool (Vibe) rather than full
     custom engineering
   - `## Legal/IP Notes` — flag if domain involves proprietary algorithms, PII,
     financial, or medical data; these require human review before AI tools are
     used in implementation
   - `## Scenarios` — ≥3 Given/When/Then (≥1 unhappy path)
   - `## Acceptance Criteria` — binary checkboxes (≥3)
   - `## Affected Domains` — OpenSPEC domains impacted
   - `## UX Applicability` — one fenced JSON object with boolean `required`
     and nonempty scope-backed `reason`; true only for affected visual surfaces
8. **Obtain proposal acceptance** — Present the proposal. Only after explicit
   acceptance, label an existing handoff PR `stage:ux` if visual, otherwise
   `stage:design`; keep the source idea issue
   labelled `stage:proposal`. Do not create a PR unless asked. No design or
   implementation before its applicable acceptance and planning prerequisites.
9. **Confirm** — Comment with link to `proposal.md`

---

## Quality Checks

- [ ] Explicit Proceed preceded the first repository write; deferred/rejected
      intake has no repository artifacts or successful archive claim
- [ ] proposal.md has the required sections, including UX Applicability,
      Build/Buy/Vibe Flag, and Legal/IP Notes
- [ ] CLI-only, API-only, and framework changes with no affected visual
      interface require no UX artifacts or UX tests; functional gates remain
- [ ] At least 3 Given/When/Then scenarios
- [ ] At least 1 unhappy path scenario
- [ ] At least 3 binary acceptance criteria
- [ ] Out of scope section is not empty
- [ ] Slug is valid kebab-case
- [ ] Intent describes outcomes and user needs, not implementation details

---

## Example Output

```text
Created: openspec/changes/add-csv-export/proposal.md
✓ Intent — explains the data export problem
✓ Scope — 3 user actions included
✓ Out of Scope — PDF export, scheduling explicitly excluded
✓ Approach — streaming CSV generation via export service
✓ Scenarios — 4 scenarios (3 happy, 1 unhappy: empty dataset)
✓ Acceptance Criteria — 5 binary checks
✓ Affected Domains — idea-capture, testing-standards
After acceptance: stage:ux if visual, otherwise stage:design
```

---

## Collaboration & Iteration Loop

- Review the latest workflow-improvement report issue before drafting new
  proposals.
- If issue/PR history is sparse, use baseline defaults and record assumptions in
  `proposal.md`.
- Feed recurring ambiguity patterns (missing scope, weak acceptance criteria,
  unclear actors) back into this skill.

## Scripts & Tools

- Use the OpenSpec CLI to create and validate the change artifacts.
- Use repository issue and PR history as evidence when available; do not invent
  requirements.

## Rules & Guidelines

- Keep the proposal implementation-agnostic and make acceptance criteria binary.
- Identify high-risk legal, security, testing, and operations concerns for
  downstream handoffs.
- Do not start implementation until the proposal, design, specs, and tasks are
  approved.

## Error Handling

| Error                | Cause                                       | Fix                                                          |
| -------------------- | ------------------------------------------- | ------------------------------------------------------------ |
| Missing requirements | The idea is too vague                       | Record assumptions and ask focused questions before drafting |
| Invalid slug         | Slug is not kebab-case                      | Normalize it and revalidate with OpenSpec                    |
| Conflicting scope    | Stakeholders describe incompatible outcomes | Surface the conflict and pause for a decision                |

## Scenarios & References

- Use the idea-capture spec and the OpenSpec proposal template as the source of
  truth.
- Cover at least one happy path and each known unhappy path in the proposal
  scenarios.

## Quick Reference

| Task               | Action                                                              |
| ------------------ | ------------------------------------------------------------------- |
| Start a proposal   | Gather problem, users, scope, scenarios, and acceptance criteria    |
| Validate artifacts | Run `openspec context --json` and the applicable validation command |
| Handoff            | After acceptance: `stage:ux` if visual, otherwise `stage:design`    |
