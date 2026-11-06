# SDLC Process — Source of Truth

> **Domain:** `sdlc-process` | **Owner:** architect  
> This spec describes the end-to-end autonomous SDLC workflow.  
> Update via `/opsx:propose` — do not edit directly.

---

## Purpose

Defines the ordered, spec-driven Software Fabric lifecycle and its stage gates.

## Overview

The **Software Fabric** is a spec-driven autonomous SDLC with ten stage personas
and a supporting OpenSpec agent. Every applicable stage feeds the next.
Visual changes require UX design; nonvisual CLI/API/framework changes go
directly to architecture without UX artifacts, specs, or tests. Legal review
is conditional on risk; no approval waives a mandatory quality gate.

```text
[Idea] ──► [Proposal] ──► [UX if visual] ──► [Delta Spec + Design]
   ──► [Tasks] ──► [Implementation] ──► [Tests incl. applicable UX]
   ──► [Security Review] ──► [Legal if high-risk] ──► [Code Review]
   ──► [CI/CD Pipeline] ──► [Deploy] ──► [Monitor & Operate]
```

---

## Requirements

### Requirement: Idea-First Development

The SDLC MUST begin with a human-authored idea captured using the idea template
before any spec, code, or design artifact is created.

#### Scenario: New feature starts with idea capture

- GIVEN a product idea or stakeholder request in natural language
- WHEN the Product Owner Agent processes it via `/opsx:propose <idea-slug>`
- THEN a `proposal.md` is created in `openspec/changes/<idea-slug>/`
- AND all required sections (intent, scope, scenarios, acceptance criteria) are
  populated
- AND no code or design work begins until the proposal is accepted

#### Scenario: Incomplete idea is rejected

- GIVEN a proposal with fewer than 3 Given/When/Then scenarios
- WHEN the Architect Agent reviews it
- THEN the proposal is returned with a `needs-more-detail` label
- AND specific missing sections are listed as comments

---

### Requirement: Spec Before Code

A complete OpenSPEC spec with scenarios MUST exist and be accepted before any
implementation task is assigned.

#### Scenario: Implementation blocked without spec

- GIVEN a developer attempts to open a PR referencing a change
- WHEN the CI orchestrator checks for `openspec/changes/<change>/tasks.md`
- THEN the PR is blocked if tasks.md is missing or has no checked-off items
- AND the PR receives a `spec-required` label

#### Scenario: Accepted proposal produces spec, design, and tasks

- GIVEN an accepted `proposal.md` with ≥3 scenarios
- WHEN the Architect Agent reviews it
- THEN a `specs/<domain>/spec.md` delta is produced for each affected domain
- AND `design.md` is produced with ADRs and a component diagram
- AND `tasks.md` is produced with numbered, atomic, ordered tasks
- AND implementation cannot begin until all three artifact types exist

---

### Requirement: Ordered Agent Handoffs

Each applicable stage MUST complete before the next begins, signalled by PR
labels. Visual changes MUST pass UX before architecture; nonvisual changes
MUST route directly to architecture. Legal-risk changes MUST pass conditional
legal review after security and before review. A `legal:blocked` change MUST
NOT advance to review or deployment.

| Stage Label       | Responsible Persona | Next Stage                      |
| ----------------- | ------------------- | ------------------------------- |
| `stage:proposal`  | Product Owner       | `stage:ux` or `stage:design`    |
| `stage:ux`        | UX Designer         | `stage:design`                  |
| `stage:design`    | Architect           | `stage:implement`               |
| `stage:implement` | Developer           | `stage:test`                    |
| `stage:test`      | QA Engineer         | `stage:security`                |
| `stage:security`  | Security Engineer   | `stage:legal` or `stage:review` |
| `stage:legal`     | Legal & Compliance  | `stage:review`                  |
| `stage:review`    | Code Reviewer       | `stage:deploy`                  |
| `stage:deploy`    | DevOps/SRE          | `stage:operate`                 |
| `stage:operate`   | Operations SRE      | `archived`                      |

#### Scenario: Stage label gates merge

- GIVEN a PR without the `stage:review` label
- WHEN a merge is attempted
- THEN the merge is blocked by a branch protection rule
- AND a comment lists the incomplete stages

#### Scenario: Legal stage is required for high-risk work

- GIVEN a change identified as having legal-risk triggers
- WHEN it completes security review
- THEN it is routed to `stage:legal` before code review
- AND `stage:review` is rejected until `legal:approved` is recorded

#### Scenario: Legal block prevents deployment

- GIVEN a pull request labelled `legal:blocked`
- WHEN `stage:deploy` is applied
- THEN the SDLC orchestrator fails the deployment gate
- AND the pull request remains blocked pending remediation or counsel sign-off

#### Scenario: Proposal hands off to UX before architecture

- GIVEN an accepted proposal affects a visual interface
- WHEN the Product Owner completes the proposal stage
- THEN work is routed to `stage:ux`
- AND the Architect does not begin until the UX Designer has produced the brief
- AND the UX Designer hands the brief to the Architect at `stage:design`

#### Scenario: Missing UX brief blocks architecture

- GIVEN a visual change labelled `stage:design` without a UX brief
- WHEN the design-stage gate validates its required artifacts
- THEN the gate blocks the Architect handoff and reports the missing UX brief

#### Scenario: Nonvisual proposal bypasses UX work

- GIVEN accepted applicability records no affected visual interface
- WHEN the Product Owner hands off the proposal
- THEN work goes directly to `stage:design`
- AND no UX stage, brief, UX-specific spec, or UX test is required
- AND ordinary functional specs, tests, and other gates remain required

#### Scenario: UX criteria and security gate remain in downstream order

- GIVEN visual implementation includes UX acceptance criteria from the brief
- WHEN the change advances through testing and security
- THEN QA validates applicable responsive, keyboard, and touch behavior
- AND security passes before review or deployment

#### Scenario: Proposal hands off to UX only when necessary

- GIVEN an accepted proposal affects a visual interface
- WHEN the Product Owner completes the proposal stage
- THEN work is routed to `stage:ux`
- AND the UX Designer hands the completed brief to `stage:design`

#### Scenario: Missing applicable UX brief blocks architecture

- GIVEN a visual change labelled `stage:design` without a completed brief
- WHEN the design gate checks artifacts
- THEN it blocks handoff and reports the missing or incomplete brief

#### Scenario: Nonvisual proposal hands off directly to architecture

- GIVEN accepted applicability records no affected visual interface
- WHEN the Product Owner completes the proposal stage
- THEN the next stage is `stage:design` without UX work
- AND a mistakenly applied `stage:ux` reports the correct route without
  demanding a UX artifact

#### Scenario: Applicable UX validation precedes security

- GIVEN implementation includes applicable visual UX criteria
- WHEN test completion or security entry is evaluated
- THEN required UX checks must pass with traceable evidence
- AND passing code coverage alone cannot satisfy UX validation
- AND security still precedes review and deployment

#### Scenario: Updated changes are checked again

- GIVEN a PR changes after applicability or UX evidence was checked
- WHEN its head is updated while a relevant stage is active
- THEN applicable gates evaluate the current artifacts again
- AND prior successful checks do not automatically satisfy changed scope

---

### Requirement: Automated Quality Gates

Every change MUST pass all quality gates before `/opsx:archive` is invoked.

**Gate checklist:**

- [ ] All CI checks green (build, lint, unit tests)
- [ ] No HIGH or CRITICAL vulnerabilities in security scan
- [ ] Code coverage ≥ 80% on new code
- [ ] At least one review approval (human or AI code-reviewer)
- [ ] All acceptance criteria in spec checked off

#### Scenario: Security gate blocks merge

- GIVEN a PR with a HIGH severity vulnerability detected by the Security Agent
- WHEN the security gate runs in CI
- THEN the PR merge is blocked
- AND a linked issue is automatically opened with remediation steps
- AND the Security Engineer Agent is assigned

#### Scenario: Coverage gate blocks merge

- GIVEN a PR where new code coverage is 65% (below 80% floor)
- WHEN the CI coverage check runs
- THEN the PR is labelled `coverage-insufficient`
- AND the QA Engineer Agent is notified to add tests

---

### Requirement: Spec Archive on Completion

When all gates pass and tasks are complete, the change delta specs MUST be
merged into the main `specs/` source of truth and the change folder archived.

#### Scenario: Successful archive

- GIVEN all tasks in `tasks.md` are checked off
- AND all quality gates have passed
- WHEN `/opsx:archive` is invoked
- THEN delta specs from `changes/<slug>/specs/` merge into `openspec/specs/`
- AND the change folder moves to `openspec/changes/archive/`
- AND the merged spec reflects the ADDED/MODIFIED/REMOVED sections

#### Scenario: Archive blocked by incomplete gates

- GIVEN a change where CI is still failing
- WHEN `/opsx:archive` is invoked
- THEN the archive is rejected with a list of failing gates
- AND no files are moved or modified

---

### Requirement: Rollback and Recovery

The SDLC MUST support rollback to the previous stable state at any stage.

#### Scenario: Failed deployment triggers rollback

- GIVEN a deployment to production that fails health checks
- WHEN the DevOps/SRE Agent detects the failure within 5 minutes
- THEN the previous version is automatically restored
- AND an incident issue is opened with `incident` and `auto-rollback` labels
- AND the Operations SRE Agent begins post-mortem analysis

---

### Requirement: Scope-Based UX Applicability

Each accepted proposal MUST record whether its change affects a visual
interface and why. Nonvisual changes MUST proceed without UX design,
UX-specific specs, briefs, or tests. Missing, invalid, duplicate, or
contradictory decisions MUST block handoff rather than imply an exemption.
Applicability MUST be checked separately for each change in a PR.

#### Scenario: CLI-only or API-only scope needs no UX artifacts

- GIVEN a proposal records no affected visual interface with a scope rationale
- WHEN architecture and testing gates run
- THEN missing UX artifacts do not fail either gate
- AND functional planning, testing, coverage, and security rules remain intact

#### Scenario: Visual scope requires UX

- GIVEN a proposal records an affected visual interface
- WHEN the proposal is accepted
- THEN work is routed through UX before architecture
- AND applicability does not exempt other mandatory gates

#### Scenario: Missing or ambiguous applicability blocks routing

- GIVEN applicability is absent, invalid, duplicated, or contradictory
- WHEN a stage gate evaluates the change
- THEN it fails with the affected proposal and needed correction
- AND does not silently select either route

#### Scenario: One nonvisual change cannot exempt another visual change

- GIVEN a PR includes one nonvisual change and one visual change
- WHEN required artifacts are evaluated
- THEN the visual change still requires its own brief and validation evidence
- AND the nonvisual change needs neither artifact

#### Scenario: Backend work in a UI repository remains nonvisual

- GIVEN a change affects only an API and does not change visual behavior
- WHEN its applicability is assessed from the accepted scope
- THEN the mere presence of frontend files does not require UX
- AND an inaccurate applicability declaration must be corrected during review

## Workflow Diagrams

### Full Software Fabric Flow

```mermaid
flowchart TD
    A([💡 Idea]) --> B[Product Owner\nproposal.md]
    B --> C{Accepted?}
    C -- No --> A
    C -- Yes --> X{Visual interface affected?}
    X -- Unknown, clarify --> B
    X -- Yes --> Y[UX Designer\nux-brief.md]
    Y --> D[Architect\ndelta specs + design.md + tasks.md]
    X -- No, no UX artifacts --> D
    D --> E[Developer\nImplementation PR]
    E --> F[QA Engineer\nTest Suites]
    F --> G{Functional gates + coverage ≥ 80%\nand applicable UX evidence pass?}
    G -- No --> E
    G -- Yes --> H[Security Engineer\nSecurity Report]
    H --> I{Clean?}
    I -- No, fix --> E
    I -- Yes, legal risk --> J[Legal & Compliance\nLegal Risk Assessment]
    I -- Yes, no legal risk --> K[Code Reviewer\nPR Review]
    J --> L{Legal approved?}
    L -- No, remediate or counsel --> E
    L -- Yes --> K
    K --> M{Approved?}
    M -- No --> E
    M -- Yes --> N[CI/CD Pipeline]
    N --> O{Gates Pass?}
    O -- No --> E
    O -- Yes --> P[DevOps/SRE\nDeploy to Staging]
    P --> Q{Smoke Tests?}
    Q -- Fail --> R[Auto-Rollback]
    R --> E
    Q -- Pass --> S[Deploy to Production]
    S --> T[Operations SRE\nMonitor & SLOs]
    T --> U[/opsx:archive]
    U --> V([✅ Production Feature])
```
