# Delta for sdlc-process

## MODIFIED Requirements

### Requirement: Idea-First Development
The SDLC MUST support a human-authored idea captured in a GitHub issue labelled `idea`
as the primary non-developer intake path. The Product Owner Agent MUST use that issue as
input to the OpenSpec proposal skill before implementation code is created. Direct
`/opsx:propose` invocation MUST remain a valid alternative for users who want to create
a proposal without first opening an idea issue. The proposal skill MUST use CLI-provided
artifact instructions and MUST stop after creating planning artifacts. Command skills
MUST require Node.js 26 or later and an available OpenSpec CLI; when unavailable, they
MUST report the prerequisite and make no artifact or implementation changes.
(Previously: The SDLC began through the `/opsx:propose <idea-slug>` prompt command.)

#### Scenario: Proposal skill creates a planning-only change
- GIVEN a user submits a feature idea and the OpenSpec CLI resolves the repository root
- WHEN the proposal skill is invoked
- THEN it creates all artifacts transitively required before implementation by the selected schema
- AND it does not modify implementation code or start the apply workflow

#### Scenario: New feature starts with idea capture
- GIVEN a product idea or stakeholder request in natural language
- WHEN the Product Owner Agent processes it through the proposal skill
- THEN a proposal is created before design or implementation begins

#### Scenario: Incomplete idea is rejected
- GIVEN a proposal has fewer than the required scenarios or acceptance criteria
- WHEN the Architect Agent reviews it
- THEN the proposal is returned for more detail and implementation remains blocked

#### Scenario: Idea issue becomes a proposal
- GIVEN a GitHub issue uses the Idea Capture form and has the `idea` label
- WHEN the Product Owner Agent invokes the proposal skill with that issue
- THEN the proposal uses the issue title, fields, labels, and discussion as its input
- AND the issue retains `idea` and `stage:proposal` until the proposal is approved

#### Scenario: Direct proposal does not require an idea issue
- GIVEN a user provides a clear feature or fix request in chat
- WHEN the user invokes `/opsx:propose`
- THEN the proposal skill creates the required planning artifacts without requiring a
	GitHub issue

#### Scenario: Missing CLI prevents changes
- GIVEN a user invokes a Software Fabric command skill without an available OpenSpec CLI
- WHEN the skill checks its prerequisites
- THEN it reports the Node.js 26+ and CLI installation requirement
- AND it does not create, modify, or archive OpenSpec artifacts

### Requirement: Ordered Agent Handoffs
Software Fabric handoffs MUST use the skills-first OpenSpec workflow. The proposal skill
creates planning artifacts, the apply skill implements approved tasks, and the verify
skill evaluates completion before existing testing, security, legal, review, and archive
gates can pass. A kickoff skill MAY coordinate these actions but MUST obtain explicit
approval after planning and before implementation.
(Previously: Stage handoffs were initiated through prompt-file command wrappers.)

#### Scenario: Kickoff pauses before implementation
- GIVEN a user begins a complete Software Fabric workflow through the kickoff skill
- WHEN planning artifacts are complete
- THEN the skill presents them for approval
- AND it does not invoke implementation until the user makes a new explicit request

#### Scenario: Stage label gates merge
- GIVEN a pull request lacks the required review-stage label
- WHEN a merge is attempted
- THEN the merge is blocked and incomplete stages are reported

#### Scenario: Legal stage is required for high-risk work
- GIVEN a change has a legal-risk trigger
- WHEN security review completes
- THEN the change is routed to `stage:legal` before code review

#### Scenario: Legal block prevents deployment
- GIVEN a pull request is labelled `legal:blocked`
- WHEN deployment is requested
- THEN the deployment gate fails and the change remains blocked