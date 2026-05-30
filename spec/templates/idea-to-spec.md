# 💡 Idea → OpenSPEC Change Template

Use this template to capture a new idea and convert it into a Software Fabric
OpenSPEC change. Copy to `spec/openspec/changes/<your-slug>/proposal.md` and fill
in all sections — or run `/opsx:propose <slug>` in VS Code Copilot and the
Product Owner Agent will guide you through each section.

---
<!-- OpenSpec metadata -->
<!-- change-slug: <kebab-case-slug> -->
<!-- domain: <affected-domain> -->
<!-- priority: P0 | P1 | P2 | P3 -->
<!-- created: YYYY-MM-DD -->
<!-- status: draft | accepted | in-progress | complete -->
---

# Proposal: <Title>

> **Change slug:** `<kebab-case-slug>`  
> **Priority:** P2  
> **Affected domains:** `idea-capture`, `<other-domains>`  
> **Submitter:** @github-username  
> **Created:** YYYY-MM-DD

---

## Intent

> *Why are we doing this? What problem does it solve or opportunity does it capture?*
> *Write 1-2 paragraphs. Be concrete — a new team member with no context should
> understand the value after reading this section.*

The [system/feature/process] currently [describe the problem or gap].
This causes [impact — user pain, lost revenue, operational cost, security risk].

We will [high-level solution] so that [who benefits] can [do what they couldn't before].
This is expected to [measurable outcome].

---

## Scope

> *What IS included in this change? Be specific.*

- [ ] [Specific deliverable 1]
- [ ] [Specific deliverable 2]
- [ ] [Specific deliverable 3]

---

## Out of Scope

> *What is explicitly NOT included? Listing this prevents scope creep.*

- [Excluded feature/concern 1]
- [Excluded feature/concern 2]

---

## Approach

> *High-level technical or UX strategy. Not implementation details — that goes in design.md.*

[Describe the approach: architectural pattern, technology choice, user interaction model,
integration strategy. Reference existing patterns in the codebase where applicable.]

---

## Scenarios

> *Write ≥ 3 Given/When/Then scenarios. Include at least 1 unhappy path.*
> *These become test cases in the QA stage.*

```
Scenario: [Happy path — main flow]
  Given  [preconditions / system state]
  When   [user action or system event]
  Then   [expected observable outcome]
  And    [secondary outcome if needed]

Scenario: [Unhappy path — error or edge case]
  Given  [preconditions that lead to the error]
  When   [action that triggers the error]
  Then   [expected error response]
  And    [expected system state after the error]

Scenario: [Boundary / edge case]
  Given  [boundary condition]
  When   [action at the boundary]
  Then   [expected behavior at the boundary]
```

---

## Acceptance Criteria

> *Verifiable, binary statements. All must be true before this change is archived.*

- [ ] [AC1: observable outcome that can be verified by a person or automated test]
- [ ] [AC2: ...]
- [ ] [AC3: ...]

---

## Stakeholders

| Role            | Name / Team     | Interest                        |
|-----------------|-----------------|---------------------------------|
| Requestor       | @username       | Submitted the idea              |
| Product Owner   | AI Agent        | Owns proposal quality           |
| Primary Users   | [Team/Persona]  | Will benefit from this change   |
| Impacted Teams  | [Team]          | May need to adapt integrations  |

---

## Success Metrics

> *How will we measure success 30 days after deployment?*

- **Primary:** [Metric and target, e.g., "CSV export used by > 100 users/week"]
- **Secondary:** [Supporting metric, e.g., "Support tickets about data export drop 30%"]
- **Guard rail:** [Metric that must NOT regress, e.g., "Page load time stays < 2s"]

---

## Technical Notes

> *Optional: Any technical constraints, risks, or unknowns the Architect should be aware of.*

- [Risk or constraint 1]
- [Risk or constraint 2]

---

## Delta Spec References

> *List the spec domains this change will modify. The Architect Agent creates
> delta spec files in `specs/<domain>/spec.md` within this change folder.*

Domains to update:
- `specs/idea-capture/spec.md` — [what changes]
- `specs/<other-domain>/spec.md` — [what changes]

---

## Linked Resources

- **GitHub Issue:** #[issue-number]
- **Design doc:** [design.md](./design.md) *(created by Architect Agent)*
- **Tasks:** [tasks.md](./tasks.md) *(created by Architect Agent)*
- **Related changes:** [link to related change slug]
