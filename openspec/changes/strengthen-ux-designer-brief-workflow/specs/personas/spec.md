# Delta for personas

## ADDED Requirements

### Requirement: UX Brief Grounds User Needs in Evidence

The UX Designer Agent MUST distinguish proposal-backed user needs from
assumptions and unknowns, and MUST request clarification when missing context
would materially change the experience requirements.

#### Scenario: Brief records user context and evidence

- **GIVEN** an accepted proposal and relevant source specifications
- **WHEN** the UX Designer Agent prepares the brief
- **THEN** it identifies the intended users and goals supported by the inputs
- **AND** it distinguishes sourced facts from assumptions and open questions

#### Scenario: Missing context could change the experience

- **GIVEN** user, task, or accessibility context is missing or conflicting
- **WHEN** resolving it could materially change the requested experience
- **THEN** the UX Designer Agent asks the Product Owner for specific
  clarification
- **AND** it does not invent user needs or advance an unresolved requirement

### Requirement: UX Brief Defines Verifiable Experience Criteria

The UX Designer Agent MUST provide scope-aligned UX acceptance criteria that
the Systems Architect can carry into the design and QA can verify.

#### Scenario: Criteria trace to approved needs

- **GIVEN** a brief describes user journeys and interface requirements
- **WHEN** the Architect and QA consume the brief
- **THEN** each UX acceptance criterion is observable and verifiable
- **AND** its user need or proposal requirement is identifiable

#### Scenario: Brief covers relevant interaction states

- **GIVEN** a journey includes asynchronous work, validation, or a recoverable
  failure
- **WHEN** the UX Designer Agent documents its experience
- **THEN** the brief describes applicable loading, empty, success, error, and
  recovery states
- **AND** excludes states that do not apply with a brief rationale

### Requirement: UX Brief Specifies Applicable Accessibility Checks

The UX Designer Agent MUST retain WCAG 2.2 AA as the accessibility target and
translate applicable accessibility needs into specific, verifiable behavior.

#### Scenario: Visual interface has actionable accessibility requirements

- **GIVEN** the proposed experience has a visual interactive interface
- **WHEN** the UX Designer Agent defines its accessibility criteria
- **THEN** it covers applicable keyboard and focus behavior, semantics and
  labels, contrast and non-color cues, zoom or reflow, error communication,
  reduced motion, and touch interaction
- **AND** each criterion is phrased so QA can verify it without claiming
  unperformed validation

#### Scenario: Accessibility dimension does not apply

- **GIVEN** an accessibility dimension is not relevant to the proposed
  interface or journey
- **WHEN** the UX Designer Agent records the brief criteria
- **THEN** it marks that dimension not applicable and gives a concise reason

### Requirement: UX Design Skill Provides a Repeatable Briefing Method

The UX Designer Agent MUST use the dedicated UX design skill to produce briefs
with consistent inputs, workflow, quality checks, and stop conditions.

#### Scenario: Skill guides brief creation

- **GIVEN** an accepted proposal is ready for UX design
- **WHEN** the UX Designer Agent creates `ux-brief.md`
- **THEN** it follows the skill's evidence-grounded workflow and quality checks
- **AND** preserves the Architect's technology ownership and QA's validation
  ownership

#### Scenario: Skill identifies a blocker

- **GIVEN** required context is missing or source requirements conflict
- **WHEN** the skill's stop conditions are met
- **THEN** the UX Designer Agent reports the specific blocker and clarification
  needed
- **AND** it does not present an incomplete brief as ready for handoff
