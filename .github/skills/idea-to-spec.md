# Skill: Idea to OpenSPEC Proposal

**Persona:** Product Owner Agent  
**Input:** Raw idea text (natural language)  
**Output:** `spec/openspec/changes/<slug>/proposal.md`

---

## When to Use This Skill

Use this skill when a user submits:
- A GitHub Issue with label `idea`
- A `/opsx:propose <description>` command
- A raw idea in chat that needs structuring

---

## Execution Steps

1. **Parse the idea** — Extract: problem statement, proposed solution, target users
2. **Generate slug** — Convert title to kebab-case (e.g., "add csv export" → `add-csv-export`)
3. **Validate slug** — Ensure kebab-case, 3–50 chars, starts with letter
4. **Create change folder** — `spec/openspec/changes/<slug>/`
5. **Load template** — Read `spec/templates/idea-to-spec.md`
6. **Clarify if needed** — Ask ≤ 3 focused questions if intent is ambiguous
7. **Write proposal.md** — Fill in all required sections:
   - `## Intent` — 1-2 paragraphs explaining why (what users need, not how to build it)
   - `## Scope` — bullet list of inclusions
   - `## Out of Scope` — bullet list of exclusions
   - `## Approach` — high-level strategy (outcomes, not implementation details)
   - `## Build/Buy/Vibe Flag` — note if problem may be better served by existing SaaS (Buy)
     or a bounded AI-generated internal tool (Vibe) rather than full custom engineering
   - `## Legal/IP Notes` — flag if domain involves proprietary algorithms, PII, financial,
     or medical data; these require human review before AI tools are used in implementation
   - `## Scenarios` — ≥3 Given/When/Then (≥1 unhappy path)
   - `## Acceptance Criteria` — binary checkboxes (≥3)
   - `## Affected Domains` — OpenSPEC domains impacted
8. **Label issue** — Apply `stage:design` label
9. **Confirm** — Comment with link to `proposal.md`

---

## Quality Checks

- [ ] proposal.md has all 7 required sections (including Build/Buy/Vibe Flag and Legal/IP Notes)
- [ ] At least 3 Given/When/Then scenarios
- [ ] At least 1 unhappy path scenario
- [ ] At least 3 binary acceptance criteria
- [ ] Out of scope section is not empty
- [ ] Slug is valid kebab-case
- [ ] Intent describes outcomes and user needs, not implementation details

---

## Example Output

```
Created: spec/openspec/changes/add-csv-export/proposal.md
✓ Intent — explains the data export problem
✓ Scope — 3 user actions included
✓ Out of Scope — PDF export, scheduling explicitly excluded
✓ Approach — streaming CSV generation via export service
✓ Scenarios — 4 scenarios (3 happy, 1 unhappy: empty dataset)
✓ Acceptance Criteria — 5 binary checks
✓ Affected Domains — idea-capture, testing-standards
Labelled: stage:design
```
