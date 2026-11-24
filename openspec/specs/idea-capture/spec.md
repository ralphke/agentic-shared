# Idea Capture — Source of Truth

> **Domain:** `idea-capture` | **Owner:** product-owner

## Purpose

Defines how raw ideas are ingested, validated, and transformed into
structured OpenSPEC proposals ready for the Software Fabric pipeline.

---

## Overview

Every Software Fabric change begins with an **idea** — a concise statement of a
problem, opportunity, or improvement. The idea-capture domain standardises how
ideas flow from raw input to an accepted proposal.

---

## Requirements

### Requirement: Idea Submission

The system MUST provide a structured mechanism for submitting new ideas.

**Accepted input channels:**

- GitHub Issue using the "💡 Idea Capture" issue template
- `/opsx:propose <idea-slug>` command in VS Code Copilot chat
- Direct creation of `openspec/changes/<slug>/proposal.md` from template

#### Scenario: Idea submitted via GitHub Issue

- GIVEN a user opens a GitHub Issue using the "💡 Idea Capture" template
- WHEN the issue is submitted with label `idea`
- THEN the SDLC Orchestrator workflow triggers the Product Owner Agent
- AND a change folder is created at `openspec/changes/<slug>/`
- AND the submitter receives a confirmation comment with a link to the change
  folder

#### Scenario: Idea submitted via chat command

- GIVEN a user types `/opsx:propose add-csv-export` in VS Code Copilot chat
- WHEN the Product Owner Agent processes the command
- THEN `openspec/changes/add-csv-export/proposal.md` is created
- AND the agent asks clarifying questions if intent is ambiguous

---

### Requirement: Minimum Viable Idea

An idea MUST contain enough information for the Product Owner Agent to produce a
complete proposal without additional human input.

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
- AND the agent proceeds autonomously to fill in scenarios and acceptance
  criteria

#### Scenario: Incomplete idea triggers clarification loop

- GIVEN an idea with only a title and vague problem statement
- WHEN the Product Owner Agent assesses it
- THEN the agent requests clarification on the missing fields via a GitHub
  comment
- AND does NOT create `proposal.md` until minimum information is provided

---

### Requirement: Proposal Structure

Every `proposal.md` MUST follow the repository OpenSpec proposal format and
include Intent, Scope, Out of Scope, Approach, at least three scenarios with one
unhappy path, at least three binary acceptance criteria, Affected Domains, and
UX Applicability.

#### Scenario: Proposal passes structure validation

- GIVEN a `proposal.md` with every required section
- WHEN the CI structure validator runs
- THEN the proposal is marked `valid` and progresses to the Architect Agent
- AND a confirmation comment lists the validated sections

#### Scenario: Proposal fails structure validation

- GIVEN a `proposal.md` missing the `## Out of Scope` section
- WHEN the CI structure validator runs
- THEN the PR is labelled `proposal-invalid`
- AND a comment lists exactly which sections are missing

---

### Requirement: Proposal records UX applicability

Every proposal MUST contain exactly one `## UX Applicability` decision with a
boolean `required` value and a nonempty scope-backed reason. Missing, invalid,
duplicate, or contradictory applicability MUST block the proposal handoff.

#### Scenario: Visual proposal records the UX route

- GIVEN an accepted proposal affects a visual interface
- WHEN the Product Owner completes proposal capture
- THEN the applicability decision is `required: true` with a scope-backed
  reason
- AND the proposal routes to UX before architecture

#### Scenario: Nonvisual proposal records the direct route

- GIVEN an accepted proposal affects only CLI, API, framework, or
  specification behavior
- WHEN the Product Owner completes proposal capture
- THEN the applicability decision is `required: false` with a scope-backed
  reason
- AND the proposal routes directly to architecture without UX artifacts

#### Scenario: Applicability is missing or contradictory

- GIVEN a proposal lacks a valid or unique applicability decision
- WHEN the proposal handoff is evaluated
- THEN handoff remains blocked
- AND the Product Owner requests the clarification needed to resolve the
  decision

---

### Requirement: Proposal acceptance precedes downstream artifacts

A captured proposal MUST remain unaccepted until an identified approver accepts
the current proposal content. Material changes to scope, scenarios, acceptance
criteria, or applicability MUST require renewed acceptance before UX or
architecture begins.

#### Scenario: Current proposal is accepted

- GIVEN an identified requester or maintainer approves the current proposal
- WHEN the Product Owner evaluates handoff readiness
- THEN the accepted revision is recorded as the basis for downstream work
- AND the applicable UX or architecture handoff may begin

#### Scenario: Proposal changes after acceptance

- GIVEN a proposal was accepted and then changed materially
- WHEN the next handoff is evaluated
- THEN the previous acceptance does not satisfy the current revision
- AND the Product Owner obtains renewed acceptance before progression

#### Scenario: Capture decision is not proposal acceptance

- GIVEN a requester authorizes repository capture of a planning artifact
- WHEN the proposal is created
- THEN capture proceeds without treating the authorization as approval
- AND implementation remains blocked until the current proposal is accepted

---

### Requirement: Idea Slug Format

Change folder names MUST follow the kebab-case slug convention.

**Rules:**

- Lowercase letters, digits, and hyphens only
- 3–50 characters
- Start with a letter
- Describe the change, not the ticket number (use `add-dark-mode`, not
  `issue-42`)

#### Scenario: Valid slug accepted

- GIVEN a slug `add-csv-export`
- WHEN the change folder is created
- THEN the folder `openspec/changes/add-csv-export/` is created successfully

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

See `openspec/templates/idea-to-spec.md` for the complete template.

Use with: `/openspec-propose <slug>` — the Product Owner Agent will use this
template to structure the conversation and produce `proposal.md`.
