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

### Requirement: Developer Agent
The Developer Agent MUST use the shared OpenSpec apply skill to select a change, retrieve
its CLI-provided context files, and implement only the pending tasks it identifies.
(Previously: The Developer Agent applied a fixed-path prompt wrapper.)

#### Scenario: Developer follows CLI-provided context
- GIVEN an approved change with pending tasks
- WHEN the Developer Agent begins implementation
- THEN it reads the context files returned by OpenSpec
- AND it marks a task complete only after its specified behavior is implemented

#### Scenario: Tasks to code without scope creep
- GIVEN `tasks.md` contains unchecked implementation tasks
- WHEN the Developer Agent implements them
- THEN only the listed tasks are implemented and checked off
- AND the PR modifies only files relevant to those tasks

#### Scenario: Developer responds to review feedback
- GIVEN a code review requests targeted changes
- WHEN the Developer Agent addresses the feedback
- THEN each requested change is implemented and explained in the review response