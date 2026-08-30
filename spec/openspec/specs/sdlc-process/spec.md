# SDLC Process — Source of Truth

> **Domain:** `sdlc-process` | **Owner:** architect  
> This spec describes the end-to-end autonomous SDLC workflow.  
> Update via `/opsx:propose` — do not edit directly.

---

## Overview

The **Software Fabric** is a spec-driven autonomous SDLC where eight specialized
AI agent personas collaborate in an ordered pipeline. Every artifact feeds the
next stage; no stage may be skipped without explicit Product Owner approval.

```
[Idea] ──► [Proposal] ──► [Delta Spec + Design] ──► [Tasks] ──► [Implementation]
   ──► [Tests] ──► [Security Review] ──► [Code Review]
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
- THEN a `proposal.md` is created in `spec/openspec/changes/<idea-slug>/`
- AND all required sections (intent, scope, scenarios, acceptance criteria) are populated
- AND no code or design work begins until the proposal is accepted

#### Scenario: Incomplete idea is rejected
- GIVEN a proposal with fewer than 3 Given/When/Then scenarios
- WHEN the Architect Agent reviews it
- THEN the proposal is returned with a `needs-more-detail` label
- AND specific missing sections are listed as comments

---

### Requirement: Spec Before Code
A complete OpenSPEC spec with scenarios MUST exist and be accepted before
any implementation task is assigned.

#### Scenario: Implementation blocked without spec
- GIVEN a developer attempts to open a PR referencing a change
- WHEN the CI orchestrator checks for `spec/openspec/changes/<change>/tasks.md`
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
Each agent stage MUST complete before the next begins, signalled by PR labels.
Legal review is a conditional gate after security review and before code review.
A change with legal-risk triggers MUST receive `stage:legal`; it may advance to
`stage:review` only after a `legal:approved` disposition is present. A change
labelled `legal:blocked` MUST NOT advance to code review or deployment.

| Stage Label              | Responsible Persona     | Next Stage           |
|--------------------------|-------------------------|----------------------|
| `stage:proposal`         | Product Owner           | `stage:design`       |
| `stage:design`           | Architect               | `stage:implement`    |
| `stage:implement`        | Developer               | `stage:test`         |
| `stage:test`             | QA Engineer             | `stage:security`     |
| `stage:security`         | Security Engineer       | `stage:legal` or `stage:review` |
| `stage:legal`            | Legal & Compliance      | `stage:review`       |
| `stage:review`           | Code Reviewer           | `stage:deploy`       |
| `stage:deploy`           | DevOps/SRE              | `stage:operate`      |
| `stage:operate`          | Operations SRE          | `archived`           |

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
- THEN delta specs from `changes/<slug>/specs/` merge into `spec/openspec/specs/`
- AND the change folder moves to `spec/openspec/changes/archive/`
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

## Workflow Diagrams

### Full Software Fabric Flow

```mermaid
flowchart TD
    A([💡 Idea]) --> B[Product Owner\nproposal.md]
    B --> C{Accepted?}
    C -- No --> A
    C -- Yes --> D[Architect\ndelta specs + design.md + tasks.md]
    D --> E[Developer\nImplementation PR]
    E --> F[QA Engineer\nTest Suites]
    F --> G{Coverage ≥ 80%?}
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
