# Delta for idea-capture

## MODIFIED Requirements

### Requirement: Idea Submission

The system MUST provide a structured mechanism for submitting new ideas.
Before repository capture, intake MUST follow the Pre-Capture Intake Decision
requirement: assess in conversation or session storage and obtain explicit
Proceed; Defer or Do not pursue MUST stop without repository writes.

**Accepted input channels:**

- GitHub Issue using the "💡 Idea Capture" issue template
- `/opsx:propose <idea-slug>` command in VS Code Copilot chat
- Direct creation of `openspec/changes/<slug>/proposal.md` from template

#### Scenario: Idea submitted via GitHub Issue

- GIVEN a user opens a GitHub Issue using the "💡 Idea Capture" template
- WHEN the issue is submitted with label `idea`
- THEN the SDLC Orchestrator workflow triggers the Product Owner Agent for assessment
- AND a change folder is created at `openspec/changes/<slug>/` only after explicit Proceed
- AND after capture the submitter receives a confirmation comment with a link to the change folder

#### Scenario: Idea submitted via chat command

- GIVEN a user types `/opsx:propose add-csv-export` in VS Code Copilot chat
- WHEN the Product Owner Agent processes the command
- THEN the agent assesses the idea and asks clarifying questions if intent is ambiguous
- AND `openspec/changes/add-csv-export/proposal.md` is created only after explicit Proceed
- AND an explicit request to create named repository artifacts supplies Proceed without a duplicate prompt

#### Scenario: Template preview is not repository capture

- GIVEN a user evaluates an idea using the proposal template outside the repository
- WHEN the user chooses Defer or Do not pursue
- THEN no repository files are created and no archive is attempted
- AND existing repository files are preserved

### Requirement: Minimum Viable Idea

An idea MUST contain enough information for the Product Owner Agent to produce a
complete proposal without additional clarification. Sufficient information MUST
NOT substitute for explicit Proceed before repository capture.

**Required idea fields:**

- **Title** — short, action-oriented (≤ 10 words)
- **Problem Statement** — what pain point or opportunity does this address?
- **Proposed Solution** — high-level approach (not implementation details)
- **Success Criteria** — how will we know this succeeded?
- **Stakeholders** — who benefits? who is affected?

#### Scenario: Complete idea generates proposal without clarification

- GIVEN an idea with all 5 required fields populated and explicit Proceed
- WHEN the Product Owner Agent processes it
- THEN `proposal.md` is generated without requiring additional clarification
- AND the agent proceeds autonomously to fill in scenarios and acceptance criteria
- AND capture alone does not accept the proposal or authorize implementation

#### Scenario: Incomplete idea triggers clarification loop

- GIVEN an idea with only a title and vague problem statement
- WHEN the Product Owner Agent assesses it
- THEN the agent requests clarification on the missing fields via a GitHub comment
- AND does NOT create `proposal.md` until minimum information and explicit Proceed are provided

#### Scenario: Complete idea without Proceed remains outside the worktree

- GIVEN an idea with all 5 required fields populated but no explicit Proceed
- WHEN the Product Owner Agent assesses it, including a P0 idea
- THEN the agent presents Proceed, Defer, and Do not pursue without repository writes
- AND missing input keeps capture paused
