# Delta for personas

## ADDED Requirements

### Requirement: UX Designer Agent

The UX Designer Agent MUST produce an evidence-grounded UX brief before
architecture only when the accepted change affects a visual user interface.
CLI-only, API-only, framework, and other nonvisual changes MUST NOT require UX
design, a UX brief, UX-specific specs, or UX tests.

#### Scenario: Accepted proposal produces a UX brief

- GIVEN a proposal accepted for UX design affecting a visual interface
- WHEN the UX Designer Agent completes its stage
- THEN the UX brief describes user flows and all user-facing screens or states
- AND identifies content and controls that must remain visible and discoverable
- AND defines responsive expectations for desktop, tablet, and mobile

#### Scenario: Nonvisual proposal requires no UX artifacts

- GIVEN accepted scope affects only CLI, API, or framework behavior
- WHEN the proposal is handed off
- THEN it goes directly to architecture without UX design, UX briefs,
  UX-specific specs, or UX tests
- AND functional planning, testing, and existing quality gates remain required

#### Scenario: UX brief defines accessible interactions

- GIVEN an experience with interactive controls
- WHEN the UX Designer Agent documents the interaction requirements
- THEN the brief requires readable content and WCAG 2.2 AA accessibility
- AND specifies keyboard operation, visible focus, and equivalent touch
  interaction
- AND does not rely on visually hidden or undiscoverable controls or content

#### Scenario: UX Designer flags an obsolete or infeasible technology

- GIVEN a proposal specifies a technology that appears obsolete or infeasible
- WHEN the UX Designer Agent identifies a substantiated concern
- THEN the UX brief flags the concern to the Systems Architect with its evidence
  and user-impact rationale
- AND the UX Designer does not select or prescribe a stack or replacement

#### Scenario: Technology choices remain with architecture

- GIVEN a UX brief raises a technology-risk concern
- WHEN the Systems Architect completes the technical design
- THEN the Architect evaluates the concern and records the stack decision and
  rationale in `design.md`
- AND the UX brief does not direct the Developer to use a technology

### Requirement: Architect Provides an Implementation-Ready Technology Handoff

The Architect MUST document the selected stack, rationale, and build and test
instructions needed to implement approved work without guessing. Applicable
UX technology flags MUST be evaluated without requiring a UX brief for
nonvisual changes.

#### Scenario: Architect supplies implementation details

- GIVEN a change requires implementation work
- WHEN the Architect completes `design.md`
- THEN it names the platform, language, framework, runtime/toolchain, and
  required dependencies as applicable
- AND provides the build and test instructions and relevant compatibility
  constraints
- AND evaluates any UX Designer technology-risk flags and records the decision
  and rationale

#### Scenario: Architecture handoff supports downstream UX validation

- GIVEN implementation tasks affect a visual interface
- WHEN the QA Engineer Agent validates the implementation
- THEN each UX acceptance criterion is covered by a test or documented device
  and interaction check
- AND checks cover applicable desktop, tablet, and mobile behavior, keyboard,
  and touch, with evidence and reasons for excluded dimensions
- AND unavailable required checks remain blocked rather than passed
- AND the change still passes the existing security gate before review or
  deployment
