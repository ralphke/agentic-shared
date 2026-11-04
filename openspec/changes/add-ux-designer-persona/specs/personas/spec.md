# Delta for personas

## ADDED Requirements

### Requirement: UX Designer Agent

The UX Designer Agent MUST turn an accepted proposal into a reviewable UX brief
covering user flows, readable content, accessibility, responsive layouts, and
interaction expectations before the Systems Architect begins design.

#### Scenario: Accepted proposal produces a UX brief

- GIVEN a proposal accepted for UX design
- WHEN the UX Designer Agent completes its stage
- THEN the UX brief describes user flows and all user-facing screens or states
- AND identifies content and controls that must remain visible and discoverable
- AND defines responsive expectations for desktop, tablet, and mobile

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

The Systems Architect MUST document the selected and justified implementation
stack and the information the Developer needs to build and test approved tasks
without choosing technologies by guesswork.

#### Scenario: Architect supplies implementation details

- GIVEN a change requires implementation work
- WHEN the Architect completes `design.md`
- THEN it names the platform, language, framework, runtime/toolchain, and
  required dependencies as applicable
- AND provides the build and test instructions and relevant compatibility
  constraints
- AND evaluates any UX Designer technology-risk flags and records the decision
  and rationale

#### Scenario: QA validates UX acceptance criteria

- GIVEN implementation tasks include interactive widgets or responsive layouts
- WHEN the QA Engineer Agent validates the implementation
- THEN each UX acceptance criterion is covered by a test or documented device
  and interaction check
- AND checks cover desktop, tablet, and mobile form factors, keyboard, and touch
- AND the change still passes the existing security gate before review or
  deployment
