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

#### Scenario: UX brief hands implementation constraints to architecture

- GIVEN a UX brief includes consumer UI implementation constraints
- WHEN the UX Designer Agent hands off to the Systems Architect
- THEN TypeScript is recorded as the default implementation language
- AND Rayfin is recorded only when the consumer architecture explicitly supports
  it
- AND the brief does not prescribe a framework or implement application code

#### Scenario: QA validates UX acceptance criteria

- GIVEN implementation tasks include interactive widgets or responsive layouts
- WHEN the QA Engineer Agent validates the implementation
- THEN each UX acceptance criterion is covered by a test or documented device
  and interaction check
- AND checks cover desktop, tablet, and mobile form factors, keyboard, and touch
- AND the change still passes the existing security gate before review or
  deployment
