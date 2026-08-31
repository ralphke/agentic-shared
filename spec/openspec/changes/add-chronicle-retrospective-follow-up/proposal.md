# Proposal: Add Chronicle Retrospective Follow-Up

> **Change slug:** `add-chronicle-retrospective-follow-up`  
> **Priority:** P2  
> **Affected domains:** `operations`  
> **Created:** 2026-08-30

---

## Intent

The Workflow Improvement Loop reports repository-level process signals, while
Chronicle can provide a maintainer with voluntary, local VS Code Chat workflow
and cost insights. The report should direct maintainers to both tools without
attempting to access or publish private session data from GitHub Actions.

## Scope

- [ ] Add a maintainer follow-up section to the workflow improvement report.
- [ ] Link the follow-up to `/chronicle tips` and `/chronicle cost-tips`.
- [ ] State that Chronicle findings are local and voluntary.

## Out of Scope

- Accessing Copilot session history from GitHub Actions.
- Publishing session data, prompts, or token usage to GitHub issues.
- Automated recommendations based on private session data.

## Scenarios

### Scenario: Retrospective report includes local Chronicle follow-up
- GIVEN the Workflow Improvement Loop creates or updates its report issue
- WHEN a maintainer reads the report
- THEN it directs the maintainer to `/chronicle tips` and `/chronicle cost-tips`
- AND it states that session-history findings remain local and voluntary

## Acceptance Criteria

- [ ] The report has a Maintainer Follow-Up section.
- [ ] The section includes both Chronicle commands.
- [ ] The section states the privacy boundary.
