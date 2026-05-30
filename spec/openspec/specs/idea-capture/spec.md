# Idea Capture — Source of Truth

> **Domain:** `idea-capture` | **Owner:** product-owner  
> Defines how raw ideas are ingested, validated, and transformed into
> structured OpenSPEC proposals ready for the Software Fabric pipeline.

---

## Overview

Every Software Fabric change begins with an **idea** — a concise statement of
a problem, opportunity, or improvement. The idea-capture domain standardises
how ideas flow from raw input to an accepted proposal.

---

## Requirements

### Requirement: Idea Submission
The system MUST provide a structured mechanism for submitting new ideas.

**Accepted input channels:**
- GitHub Issue using the "💡 Idea Capture" issue template
- `/opsx:propose <idea-slug>` command in VS Code Copilot chat
- Direct creation of `spec/openspec/changes/<slug>/proposal.md` from template

#### Scenario: Idea submitted via GitHub Issue
- GIVEN a user opens a GitHub Issue using the "💡 Idea Capture" template
- WHEN the issue is submitted with label `idea`
- THEN the SDLC Orchestrator workflow triggers the Product Owner Agent
- AND a change folder is created at `spec/openspec/changes/<slug>/`
- AND the submitter receives a confirmation comment with a link to the change folder

#### Scenario: Idea submitted via chat command
- GIVEN a user types `/opsx:propose add-csv-export` in VS Code Copilot chat
- WHEN the Product Owner Agent processes the command
- THEN `spec/openspec/changes/add-csv-export/proposal.md` is created
- AND the agent asks clarifying questions if intent is ambiguous

---

### Requirement: Minimum Viable Idea
An idea MUST contain enough information for the Product Owner Agent to produce
a complete proposal without additional human input.

**Required idea fields:**
- **Title** — short, action-oriented (≤ 10 words)
- **Problem Statement** — what pain point or opportunity does this address?
- **Proposed Solution** — high-level approach (not implementation details)
- **Success Criteria** — how will we know this succeeded?
- **Stakeholders** — who benefits? who is affected?

#### Scenario: Complete idea generates proposal without clarification
- GIVEN an idea with all 5 required fields populated
- WHEN the Product Owner Agent processes it
- THEN `proposal.md` is generated without requiring additional human input
- AND the agent proceeds autonomously to fill in scenarios and acceptance criteria

#### Scenario: Incomplete idea triggers clarification loop
- GIVEN an idea with only a title and vague problem statement
- WHEN the Product Owner Agent assesses it
- THEN the agent requests clarification on the missing fields via a GitHub comment
- AND does NOT create `proposal.md` until minimum information is provided

---

### Requirement: Proposal Structure
Every `proposal.md` MUST follow the OpenSPEC proposal format.

**Required sections:**
1. `## Intent` — why we are doing this (1-2 paragraphs)
2. `## Scope` — what IS included (bulleted list)
3. `## Out of Scope` — what is explicitly excluded (bulleted list)
4. `## Approach` — high-level technical or UX strategy
5. `## Scenarios` — ≥ 3 Given/When/Then scenarios (including ≥ 1 unhappy path)
6. `## Acceptance Criteria` — verifiable, binary checks (minimum 3)
7. `## Affected Domains` — which OpenSPEC domains this change touches

#### Scenario: Proposal passes structure validation
- GIVEN a `proposal.md` with all 7 required sections
- WHEN the CI structure validator runs
- THEN the proposal is marked `valid` and progresses to the Architect Agent
- AND a confirmation comment lists the validated sections

#### Scenario: Proposal fails structure validation
- GIVEN a `proposal.md` missing the `## Out of Scope` section
- WHEN the CI structure validator runs
- THEN the PR is labelled `proposal-invalid`
- AND a comment lists exactly which sections are missing

---

### Requirement: Idea Slug Format
Change folder names MUST follow the kebab-case slug convention.

**Rules:**
- Lowercase letters, digits, and hyphens only
- 3–50 characters
- Start with a letter
- Describe the change, not the ticket number (use `add-dark-mode`, not `issue-42`)

#### Scenario: Valid slug accepted
- GIVEN a slug `add-csv-export`
- WHEN the change folder is created
- THEN the folder `spec/openspec/changes/add-csv-export/` is created successfully

#### Scenario: Invalid slug rejected
- GIVEN a slug `Issue #42 fix!`
- WHEN the change folder creation is attempted
- THEN an error is returned listing the slug format rules

---

### Requirement: Idea Prioritization
The Product Owner Agent MUST maintain a prioritized backlog.

**Priority levels:**
- `P0` — Critical: security incident, data loss, service outage
- `P1` — High: user-facing bug, major feature request
- `P2` — Medium: improvement, minor feature
- `P3` — Low: polish, tech debt, nice-to-have

#### Scenario: P0 idea bypasses queue
- GIVEN a P0 idea (e.g., security vulnerability)
- WHEN the Product Owner Agent receives it
- THEN it is immediately prioritized ahead of all other in-flight changes
- AND all other non-P0 stages are paused if resources conflict

---

## Idea-to-Proposal Template Reference

See `spec/templates/idea-to-spec.md` for the complete template.

Use with: `/opsx:propose <slug>` — the Product Owner Agent will use this template
to structure the conversation and produce `proposal.md`.
