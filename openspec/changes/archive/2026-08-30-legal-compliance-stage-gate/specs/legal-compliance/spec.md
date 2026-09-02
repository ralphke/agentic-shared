# Delta for legal-compliance

## MODIFIED Requirements

### Requirement: Legal Gate Handoff
An approved legal assessment MUST be represented by the `legal:approved` pull
request label before the work enters `stage:review`. A `legal:blocked` label
MUST prevent review and deployment until the recorded remediation or qualified
legal counsel disposition resolves the block.

#### Scenario: Approved disposition is explicitly recorded
- GIVEN a completed legal assessment with an `APPROVE` decision
- WHEN the Legal & Compliance Agent completes the handoff
- THEN it applies the `legal:approved` label before `stage:review`
- AND the SDLC orchestrator permits code review to begin

#### Scenario: Blocked disposition prevents later stages
- GIVEN a pull request with the `legal:blocked` label
- WHEN a reviewer applies `stage:review` or `stage:deploy`
- THEN the SDLC orchestrator fails the selected stage gate
- AND the pull request remains blocked pending legal remediation