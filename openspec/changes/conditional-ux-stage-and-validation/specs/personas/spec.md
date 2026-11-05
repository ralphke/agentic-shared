# Delta for personas

## ADDED Requirements

### Requirement: UX Designer Agent

The UX Designer Agent MUST produce an evidence-grounded UX brief before
architecture only when the accepted change affects a visual user interface.
CLI-only, API-only, framework, and other nonvisual changes MUST NOT require UX
design, a UX brief, UX-specific specs, or UX tests.

#### Scenario: Visual change receives UX design

- GIVEN an accepted proposal affects a visual interface
- WHEN the Product Owner hands off the proposal
- THEN it is routed to the UX Designer at `stage:ux`
- AND the Designer creates `ux-brief.md` before `stage:design`
- AND the brief covers affected journeys, states, content, discoverability,
  accessibility, and responsive interactions

#### Scenario: Nonvisual change bypasses UX without extra artifacts

- GIVEN an accepted CLI-only, API-only, or framework change affects no visual
  interface
- WHEN the Product Owner hands off the proposal
- THEN it goes directly to the Architect at `stage:design`
- AND no UX stage, brief, UX-specific spec, or UX test is required
- AND functional planning, testing, and existing quality gates still apply

#### Scenario: Mixed scope limits UX to affected visual surfaces

- GIVEN a change affects both visual and nonvisual behavior
- WHEN the UX Designer prepares the brief
- THEN UX requirements cover the affected visual surfaces
- AND no nonvisual UX obligations are invented for the remaining behavior

#### Scenario: UX Designer flags an obsolete or infeasible technology

- GIVEN a proposal specifies a technology that appears obsolete or infeasible
- WHEN the UX Designer identifies a substantiated concern
- THEN the brief flags it with evidence and user-impact rationale
- AND the Designer does not select or prescribe a stack or replacement

#### Scenario: Technology choices remain with architecture

- GIVEN a UX brief raises a technology-risk concern
- WHEN the Architect completes the technical design
- THEN the Architect records the stack decision and rationale in `design.md`
- AND the brief does not direct the Developer to use a technology

### Requirement: UX Brief Grounds User Needs in Evidence

For applicable visual changes, the UX Designer MUST distinguish sourced user
needs from assumptions and unknowns, and MUST request clarification when
missing context could materially change the experience.

#### Scenario: Brief records user context and evidence

- GIVEN an accepted visual proposal and relevant source specifications
- WHEN the Designer prepares the brief
- THEN intended users and goals trace to those inputs
- AND sourced facts, assumptions, and open questions remain distinct

#### Scenario: Missing context could change the experience

- GIVEN user, task, or accessibility context is missing or conflicting
- WHEN resolving it could materially change the experience
- THEN the Designer asks the Product Owner for specific clarification
- AND does not invent user needs or advance an unresolved requirement

### Requirement: UX Brief Defines Verifiable Experience Criteria

For applicable visual changes, the UX Designer MUST provide scope-aligned,
observable UX criteria with stable IDs and identifiable source needs that
architecture preserves and QA verifies.

#### Scenario: Criteria trace to approved needs

- GIVEN a brief describes affected journeys and interface requirements
- WHEN architecture and QA consume it
- THEN each UX criterion has a stable ID and identifiable source need
- AND the criterion states an observable, verifiable outcome

#### Scenario: Brief covers relevant interaction states

- GIVEN a visual journey includes asynchronous work or recoverable failure
- WHEN the Designer documents the experience
- THEN applicable loading, empty, success, error, and recovery states are
  specified
- AND excluded states have a concise applicability rationale

### Requirement: UX Brief Specifies Applicable Accessibility Checks

For visual changes, the UX Designer MUST retain WCAG 2.2 AA as the target and
express applicable accessibility dimensions as verifiable behavior.
Inapplicable dimensions MUST have reasons; no check may be claimed performed
without validation evidence.

#### Scenario: Visual interface has actionable accessibility requirements

- GIVEN a visual interactive interface is affected
- WHEN the Designer defines accessibility criteria
- THEN applicable keyboard, focus, semantics, labels, contrast, non-color cues,
  zoom or reflow, error communication, reduced motion, and touch are covered
- AND QA can verify each criterion without guessing expected behavior

#### Scenario: Accessibility dimension does not apply

- GIVEN an accessibility dimension is irrelevant to the affected surface
- WHEN the Designer records the criteria
- THEN that dimension is marked not applicable with a concise reason
- AND this exclusion is not presented as evidence of conformance

### Requirement: UX Design Skill Provides a Repeatable Briefing Method

The UX Designer MUST use the dedicated UX design skill for applicable visual
briefs. The skill MUST stop without creating UX artifacts for nonvisual
changes and MUST preserve architecture's technology ownership and QA's
validation ownership.

#### Scenario: Skill guides brief creation

- GIVEN an accepted visual proposal is ready for UX design
- WHEN the Designer creates the brief
- THEN the skill's evidence-grounded workflow and checks are followed
- AND technology selection and validation stay with their respective owners

#### Scenario: Skill receives a nonvisual change

- GIVEN accepted applicability states that no visual interface is affected
- WHEN the UX skill is invoked
- THEN it creates no UX brief or other UX artifact
- AND directs the work to architecture using the existing proposal decision

#### Scenario: Skill identifies a blocker

- GIVEN required context is missing or source requirements conflict
- WHEN the skill's stop conditions are met
- THEN the specific blocker and clarification needed are reported
- AND the brief is not presented as ready

### Requirement: Architect Provides an Implementation-Ready Technology Handoff

The Architect MUST document the selected stack, rationale, and build and test
instructions needed to implement approved work without guessing. Applicable
UX technology flags MUST be evaluated without requiring a UX brief for
nonvisual changes.

#### Scenario: Architect supplies implementation details

- GIVEN a change requires implementation work
- WHEN the Architect completes `design.md`
- THEN platform, language, framework, toolchain, dependencies, compatibility,
  and build and test instructions are supplied as applicable
- AND any UX technology-risk flags have a recorded decision and rationale

## MODIFIED Requirements

### Requirement: Product Owner Agent

The Product Owner Agent SHALL capture explicit acceptance criteria that include
quality measurement expectations when a change targets skill definition
standards. The Product Owner MUST record scope-backed UX applicability in the
accepted proposal and route visual changes to UX and nonvisual changes directly
to architecture.

#### Scenario: Skill-standard change includes measurable acceptance criteria

- GIVEN a proposal targets skill definition standards
- WHEN the Product Owner Agent prepares the proposal
- THEN the acceptance criteria include instruction completeness, ambiguity
  reduction, and checklist coverage measures
- AND the proposal identifies the required baseline and post-change evaluation
  evidence

#### Scenario: Idea to structured proposal

- GIVEN a raw idea is submitted through an approved intake channel
- WHEN the Product Owner Agent processes it
- THEN `proposal.md` contains intent, scope, scenarios, and acceptance criteria
- AND at least one unhappy-path scenario is included

#### Scenario: Proposal requires minimum scenario count

- GIVEN a proposal has fewer than 3 scenarios
- WHEN the Architect Agent reviews it
- THEN the proposal is returned for more detail
- AND it is not approved until the minimum scenario count is met

#### Scenario: Applicability cannot be guessed

- GIVEN the affected visual scope is missing or contradictory
- WHEN the Product Owner prepares the handoff
- THEN clarification is required before selecting a route
- AND missing evidence is not treated as a nonvisual exemption

### Requirement: Systems Architect Agent

The Architect Agent MUST translate accepted proposals into technical designs.

**Responsibilities:**

- Review proposals for technical feasibility and alignment with existing system
- Read `ux-brief.md` only when accepted applicability requires UX
- Preserve applicable UX criteria in design, delta specs, and QA tasks
- Produce `design.md` with selected technology, component diagrams (Mermaid),
  ADRs
- Identify all integration points, API contracts, and data model changes
- Decompose design into atomic, ordered, estimated tasks in `tasks.md`
- Ensure non-functional requirements (performance, scalability) are addressed
- Translate the accepted proposal into OpenSpec delta specs for affected domains

**Input:** `proposal.md`, existing system specs, codebase structure, and a UX
brief only for applicable visual changes  
**Output:** `design.md`, delta specs in `specs/<domain>/spec.md`, `tasks.md`,
Architecture Decision Records (ADRs) **Triggers:** `stage:design` after the
applicable proposal or UX handoff  
**Handoff:** Labels PR `stage:implement` when design is accepted  
**Agent file:** `.github/agents/architect.agent.md`

#### Scenario: Proposal to technical design

- GIVEN a complete `proposal.md` with at least 3 scenarios
- WHEN the Architect Agent reviews it
- THEN `design.md` includes chosen stack with rationale, Mermaid component
  diagram, data model, API contract, and ADRs for key decisions
- AND `tasks.md` contains numbered, atomic tasks with size estimates (S/M/L)

#### Scenario: Design identifies breaking change

- GIVEN a design that requires a breaking API change
- WHEN the Architect Agent documents it
- THEN an ADR records the breaking change, migration path, and deprecation plan
- AND the proposal scope includes migration tasks

#### Scenario: Architect requires only applicable UX inputs

- GIVEN accepted applicability states no visual interface is affected
- WHEN architecture begins
- THEN missing UX artifacts do not block design
- AND normal functional specs and testing tasks remain required

### Requirement: Developer Agent

The Developer Agent MUST implement tasks from the approved design.

**Responsibilities:**

- Implement only approved tasks in `tasks.md` without scope creep
- Follow project coding standards and conventions
- Preserve UX criteria for applicable visual work without requiring UX inputs
  for nonvisual work
- Write implementation code with documentation for non-obvious logic
- Open a PR per logical task group referencing the change slug
- Respond to code review feedback with targeted fixes within the same PR

**Input:** `tasks.md`, `design.md`, existing codebase, and a UX brief only when
applicable  
**Output:** Source code and a PR linking to the change folder  
**Triggers:** `stage:implement`  
**Handoff:** Labels PR `stage:test` when implementation tasks are checked off  
**Agent file:** `.github/agents/developer.agent.md`

#### Scenario: Tasks to code without scope creep

- GIVEN `tasks.md` with 5 unchecked implementation tasks
- WHEN the Developer Agent implements them
- THEN exactly those 5 tasks are implemented and checked off
- AND the PR modifies only relevant files
- AND its description includes `Implements: openspec/changes/<slug>/`

#### Scenario: Developer responds to review feedback

- GIVEN a code review with 3 requested changes
- WHEN the Developer addresses them
- THEN each is addressed in a follow-up commit
- AND each reviewer comment receives an explanation

### Requirement: QA Engineer Agent

The QA Engineer Agent MUST create and validate automated tests from spec
scenarios.

**Responsibilities:**

- Generate tests directly from Given/When/Then scenarios in `spec.md`
- Write unit, integration, and end-to-end tests as appropriate
- Achieve at least 80% coverage on new code
- Include negative, boundary, and performance tests
- Ensure automated tests run in CI without manual steps
- Map applicable visual UX criteria to tests or documented interaction and
  device checks, recording results and evidence without unsupported claims
- Require no UX brief, UX-specific specs, or UX tests for nonvisual changes
- Update only Testing Tasks in the Architect-owned `tasks.md`

**Input:** Spec scenarios, source code, and UX criteria only when applicable  
**Output:** Test suites, coverage report, testing-task updates, and UX
validation evidence only when applicable  
**Triggers:** `stage:test`  
**Handoff:** Labels PR `stage:security` when functional and applicable UX
validation gates pass  
**Agent file:** `.github/agents/qa-engineer.agent.md`

#### Scenario: Spec scenarios become test cases

- GIVEN `spec.md` with N Given/When/Then scenarios
- WHEN QA generates test suites
- THEN at least N deterministic tests exist and pass in CI
- AND coverage reports at least 80% for new code paths

#### Scenario: Missing test coverage triggers rework

- GIVEN new-code coverage is below 80%
- WHEN QA checks coverage
- THEN the PR is labelled `coverage-insufficient`
- AND a comment lists uncovered paths

#### Scenario: QA validates UX acceptance criteria

- GIVEN implementation affects a visual interface
- WHEN QA validates the implementation
- THEN each UX criterion maps to a passing test or documented check
- AND applicable responsive, keyboard, touch, accessibility, and state
  behavior has recorded evidence
- AND unavailable required checks remain unresolved rather than passed

#### Scenario: QA validates a nonvisual implementation

- GIVEN accepted scope affects only CLI, API, or framework behavior
- WHEN QA plans and runs tests
- THEN functional scenarios, negative cases, and coverage remain required
- AND no UX artifact, UX test, or frontend tooling is required
