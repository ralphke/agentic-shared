# Delta for personas

## ADDED Requirements

### Requirement: Skills Standards Compliance Plan MUST Be Approved Before Execution
Changes that standardize skill definitions SHALL begin with a reviewed proposal and explicit approval before implementation tasks are executed.

#### Scenario: Proposal blocks implementation until approval
- GIVEN a change folder for skill standards exists under `openspec/changes/<slug>/`
- WHEN `proposal.md` status is draft or unapproved
- THEN implementation tasks in `tasks.md` remain unchecked
- AND no changes are made to production skill definitions outside planning artifacts

### Requirement: Skill Quality Improvements MUST Be Measured Against Baseline
Skill optimization changes SHALL include baseline and post-change evaluation artifacts with measurable comparison output.

#### Scenario: Relative improvement threshold is evaluated
- GIVEN baseline metrics captured without skill assistance
- WHEN post-change metrics are captured with updated skills
- THEN a summary compares baseline versus post-change values
- AND the change records whether the relative improvement target (>=5% where measurable) is achieved

### Requirement: Persona Definitions MUST Follow a Consistent Standard Layout
Persona files under `.github/agents/` SHALL follow a consistent layout so stage handoffs and execution expectations remain predictable.

#### Scenario: Persona layout audit enforces consistency
- GIVEN persona files in `.github/agents/*.agent.md`
- WHEN a standards alignment change is prepared
- THEN each persona file includes consistent sections for role intent, core responsibilities, behavior rules, execution/checklist guidance, and handoff protocol
- AND deviations are captured as tasks before implementation completion

## MODIFIED Requirements

### Requirement: Product Owner Agent
The Product Owner Agent SHALL capture explicit acceptance criteria that include quality measurement expectations when a change targets skill definition standards.
(Previously: The Product Owner Agent is the entry point for all new work.)

#### Scenario: Skill-standard change includes measurable acceptance criteria
- GIVEN a proposal targets skill definition standards
- WHEN the Product Owner Agent prepares the proposal
- THEN the acceptance criteria include instruction completeness, ambiguity reduction, and checklist coverage measures
- AND the proposal identifies the required baseline and post-change evaluation evidence

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

## REMOVED Requirements
