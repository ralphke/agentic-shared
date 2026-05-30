# Personas — Source of Truth

> **Domain:** `personas` | **Owner:** architect  
> Defines all Software Fabric agent personas, their responsibilities, inputs,
> outputs, tools, and collaboration contracts.

---

## Overview

The Software Fabric consists of **8 specialized agent personas**. Each persona
owns a distinct SDLC stage and produces artifacts consumed by the next persona.
Personas are defined in `.github/agents/` and referenced by Copilot instructions.

---

## Persona Definitions

### Requirement: Product Owner Agent

The Product Owner (PO) Agent is the entry point for all new work.

**Responsibilities:**
- Accept raw ideas via GitHub issues (label: `idea`) or `/opsx:propose`
- Produce a complete OpenSPEC `proposal.md` covering intent, scope, user value
- Define ≥ 3 Given/When/Then scenarios per feature, including unhappy paths
- Identify explicitly out-of-scope items to prevent scope creep
- Maintain the overall product backlog and prioritization

**Input:** Raw idea text, user story, business requirement, customer feedback  
**Output:** `proposal.md`, initial delta `specs/<domain>/spec.md`  
**Triggers:** GitHub issue with label `idea`, `/opsx:propose <slug>` command  
**Handoff:** Labels PR/issue `stage:design` when proposal is accepted  
**Agent file:** `.github/agents/product-owner.md`

#### Scenario: Idea to structured proposal
- GIVEN a raw idea: "Users should be able to export their data as CSV"
- WHEN the Product Owner Agent processes it
- THEN `proposal.md` contains: intent paragraph, scope list, ≥3 scenarios, acceptance criteria
- AND at least one unhappy-path scenario is included (e.g., empty data set, large export)
- AND out-of-scope items are explicitly listed (e.g., PDF export, scheduling)

#### Scenario: Proposal requires minimum scenario count
- GIVEN a proposal with only 2 scenarios
- WHEN the Architect Agent reviews it
- THEN a `needs-more-detail` comment is added requesting more scenarios
- AND the proposal is NOT approved until the minimum is met

---

### Requirement: Systems Architect Agent

The Architect Agent translates accepted proposals into technical designs.

**Responsibilities:**
- Review proposals for technical feasibility and alignment with existing system
- Produce `design.md` with selected technology, component diagrams (Mermaid), ADRs
- Identify all integration points, API contracts, and data model changes
- Decompose design into atomic, ordered, estimated tasks in `tasks.md`
- Ensure non-functional requirements (performance, scalability) are addressed

**Input:** `proposal.md`, existing system specs, codebase structure  
**Output:** `design.md`, `tasks.md`, Architecture Decision Records (ADRs)  
**Triggers:** Proposal labelled `stage:design`  
**Handoff:** Labels PR `stage:implement` when design is accepted  
**Agent file:** `.github/agents/architect.md`

#### Scenario: Proposal to technical design
- GIVEN a complete `proposal.md` with ≥3 scenarios
- WHEN the Architect Agent reviews it
- THEN `design.md` includes: chosen tech stack with rationale, Mermaid component diagram,
  data model schema, API contract (request/response), ADRs for key decisions
- AND `tasks.md` contains numbered, atomic tasks with size estimates (S/M/L)

#### Scenario: Design identifies breaking change
- GIVEN a design that requires a breaking API change
- WHEN the Architect Agent documents it
- THEN an ADR is created noting the breaking change, migration path, and deprecation plan
- AND the proposal scope is updated to include migration tasks

---

### Requirement: Developer Agent

The Developer Agent implements tasks from the approved design.

**Responsibilities:**
- Implement ONLY tasks listed in `tasks.md` — no scope creep
- Follow project coding standards and conventions
- Write implementation code with documentation for non-obvious logic
- Open a PR per logical task group with a description referencing the change slug
- Respond to code review feedback with targeted fixes within the same PR

**Input:** `tasks.md`, `design.md`, existing codebase  
**Output:** Source code, PR with description linking to change folder  
**Triggers:** Tasks labelled `stage:implement`  
**Handoff:** Labels PR `stage:test` when all implementation tasks are checked off  
**Agent file:** `.github/agents/developer.md`

#### Scenario: Tasks to code without scope creep
- GIVEN `tasks.md` with 5 unchecked implementation tasks
- WHEN the Developer Agent implements them
- THEN exactly the 5 tasks are implemented and checked off
- AND the PR modifies only files relevant to those tasks
- AND the PR description includes `Implements: spec/openspec/changes/<slug>/`

#### Scenario: Developer responds to review feedback
- GIVEN a code review with 3 requested changes
- WHEN the Developer Agent addresses them
- THEN each requested change is addressed in a follow-up commit
- AND each reviewer comment is replied to explaining what was done

---

### Requirement: QA Engineer Agent

The QA Engineer Agent creates and validates automated tests from spec scenarios.

**Responsibilities:**
- Generate test cases directly from Given/When/Then scenarios in `spec.md`
- Write unit tests, integration tests, and e2e tests as appropriate
- Achieve ≥ 80% code coverage on all new code
- Include negative, boundary, and performance tests
- Ensure all tests are automated and run in CI without manual steps

**Input:** `spec.md` scenarios, source code from Developer Agent  
**Output:** Test suites, coverage report, updated `tasks.md`  
**Triggers:** PR labelled `stage:test`  
**Handoff:** Labels PR `stage:security` when coverage gate passes  
**Agent file:** `.github/agents/qa-engineer.md`

#### Scenario: Spec scenarios become test cases
- GIVEN `spec.md` with N Given/When/Then scenarios
- WHEN the QA Agent generates test suites
- THEN ≥ N test cases exist (at least one per scenario)
- AND all tests are deterministic and pass in CI
- AND coverage report shows ≥ 80% for new code paths

#### Scenario: Missing test coverage triggers rework
- GIVEN a PR where new code coverage is below 80%
- WHEN the QA Agent's coverage check runs
- THEN the PR is labelled `coverage-insufficient`
- AND a comment lists the uncovered code paths

---

### Requirement: Security Engineer Agent

The Security Engineer Agent ensures every change is free of exploitable vulnerabilities.

**Responsibilities:**
- Run SAST (static analysis) on all new and changed code
- Audit all dependency changes for CVEs using SBOM/dependency scan
- Review authentication and authorization logic against OWASP Top 10
- Validate input sanitization, output encoding, and secret management
- Produce a security report; block merge on HIGH/CRITICAL findings

**Input:** PR diff, dependency manifest, SBOM  
**Output:** Security report, vulnerability list with CVSS scores, remediation tasks  
**Triggers:** PR labelled `stage:security`  
**Handoff:** Labels PR `stage:review` when security gate passes  
**Agent file:** `.github/agents/security-engineer.md`

#### Scenario: Clean security scan allows progression
- GIVEN a PR with no HIGH or CRITICAL vulnerabilities
- WHEN the Security Agent completes the scan
- THEN the PR is labelled `security:passed`
- AND a summary comment lists scan results (even if all LOW/INFO)

#### Scenario: HIGH vulnerability blocks merge
- GIVEN a PR introducing a dependency with a known HIGH CVE
- WHEN the Security Agent scans dependencies
- THEN the PR is labelled `security:blocked`
- AND merge is prevented by a CI gate
- AND a linked issue is opened with the CVE ID, CVSS score, and remediation options

---

### Requirement: Code Reviewer Agent

The Code Reviewer Agent validates code quality, design alignment, and best practices.

**Responsibilities:**
- Review code against `design.md` requirements and specifications
- Check naming conventions, complexity (cyclomatic), and duplication
- Verify error handling, logging patterns, and observability hooks
- Validate inline documentation and public API contracts
- Provide specific, actionable feedback — never vague comments

**Input:** PR diff, `design.md`, coding standards  
**Output:** PR review (APPROVE / REQUEST_CHANGES), inline comments  
**Triggers:** PR labelled `stage:review`  
**Handoff:** Approves PR to trigger `stage:deploy`  
**Agent file:** `.github/agents/code-reviewer.md`

#### Scenario: Review produces actionable comments
- GIVEN a PR with unclear variable names and missing error handling
- WHEN the Code Reviewer Agent reviews it
- THEN each comment references a specific line with a suggested fix
- AND each comment explains WHY it matters (readability, reliability, etc.)

#### Scenario: Review approval enables deployment
- GIVEN all inline comments are addressed by the Developer Agent
- WHEN the Code Reviewer Agent re-reviews
- THEN the PR is approved with a summary of what was checked

---

### Requirement: DevOps/SRE Agent

The DevOps/SRE Agent automates infrastructure provisioning and staged deployment.

**Responsibilities:**
- Validate and update CI/CD pipeline configuration for the change
- Provision or update infrastructure using IaC (Bicep, Terraform, or Docker Compose)
- Execute staged deployments: dev → staging → production
- Run smoke tests after each deployment stage; auto-rollback on failure
- Update deployment runbooks and environment documentation

**Input:** Approved PR, infrastructure spec, IaC templates  
**Output:** Deployed application, deployment report, updated runbooks  
**Triggers:** PR approved by Code Reviewer (label: `stage:deploy`)  
**Handoff:** Labels issue `stage:operate` after successful production deploy  
**Agent file:** `.github/agents/devops-sre.md`

#### Scenario: Successful staged deployment
- GIVEN an approved PR
- WHEN the DevOps Agent deploys to staging
- THEN smoke tests run automatically against the staging environment
- AND IF smoke tests pass, production deployment begins
- AND a deployment summary comment is added to the PR

#### Scenario: Failed staging triggers rollback
- GIVEN a staging deployment where 3+ smoke tests fail
- WHEN the DevOps Agent detects failures within 5 minutes
- THEN the previous staging version is automatically restored
- AND an incident issue is opened with `incident` and `deploy-failed` labels

---

### Requirement: Operations/SRE Agent

The Operations SRE Agent ensures the deployed application is observable and resilient.

**Responsibilities:**
- Configure monitoring dashboards for new features and endpoints
- Define and register SLOs (availability, latency, error rate) for new surfaces
- Create alert policies for SLO violation thresholds
- Maintain and update runbooks for new operational scenarios
- Lead post-mortems and propose SDLC improvements from operational learnings

**Input:** Deployed application, SLO targets, existing dashboards  
**Output:** Monitoring dashboards, alert policies, runbooks, post-mortem reports  
**Triggers:** Successful production deployment (label: `stage:operate`)  
**Handoff:** Invokes `/opsx:archive` when SLOs are configured and stable  
**Agent file:** `.github/agents/operations-sre.md`

#### Scenario: New endpoint gets SLO and alerting
- GIVEN a new API endpoint deployed to production
- WHEN the Operations Agent configures observability
- THEN a dashboard panel is created for the endpoint
- AND an SLO target is defined (e.g., p99 latency < 500ms, availability > 99.9%)
- AND an alert fires when the SLO is violated for > 5 minutes

---

## Collaboration Contract

All personas MUST follow this contract when handing off work:

1. **Update `tasks.md`** — check off completed items before handoff
2. **Label the PR** — set the appropriate `stage:*` label
3. **Comment on the PR** — provide a handoff summary with findings and blockers
4. **Create sub-issues for blockers** — link to the main PR
5. **Never skip a stage** — if a stage is not applicable, document why in a comment
