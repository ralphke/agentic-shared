# Delta for operations

## ADDED Requirements

### Requirement: Workflow Retrospective Maintainer Follow-Up
Workflow retrospective reports MUST distinguish repository-level telemetry from
optional, local developer-session analysis. Reports SHOULD direct maintainers to
`/chronicle tips` and `/chronicle cost-tips` without collecting or publishing
Copilot session content or token-usage data.

#### Scenario: Report preserves the session-data boundary
- GIVEN the Workflow Improvement Loop creates or updates its report issue
- WHEN a maintainer reviews the report
- THEN it includes optional Chronicle follow-up commands
- AND it states that session-history findings are local and voluntary