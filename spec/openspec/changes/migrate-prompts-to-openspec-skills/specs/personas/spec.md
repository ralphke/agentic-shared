# Delta for personas

## MODIFIED Requirements

### Requirement: Product Owner Agent
The Product Owner Agent MUST use the shared OpenSpec proposal skill for new work. The
skill MUST preserve the planning-only boundary, use CLI-resolved artifact paths and
instructions, and route completed planning artifacts to the Architect handoff.
(Previously: The Product Owner Agent accepted raw ideas through a prompt-file command.)

#### Scenario: Product Owner uses the proposal skill
- GIVEN a raw idea requiring a Software Fabric change
- WHEN the Product Owner Agent starts planning
- THEN it uses the proposal skill and OpenSpec CLI workflow state
- AND it produces the proposal, delta specs, design, and tasks required for apply

### Requirement: Developer Agent
The Developer Agent MUST use the shared OpenSpec apply skill to select a change, retrieve
its CLI-provided context files, and implement only the pending tasks it identifies.
(Previously: The Developer Agent applied a fixed-path prompt wrapper.)

#### Scenario: Developer follows CLI-provided context
- GIVEN an approved change with pending tasks
- WHEN the Developer Agent begins implementation
- THEN it reads the context files returned by OpenSpec
- AND it marks a task complete only after its specified behavior is implemented