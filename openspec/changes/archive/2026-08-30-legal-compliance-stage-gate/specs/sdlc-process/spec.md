# Delta for sdlc-process

## MODIFIED Requirements

### Requirement: Ordered Agent Handoffs
Legal review MUST be a conditional gate after security review and before code
review. A change with legal-risk triggers MUST receive `stage:legal`; it may
advance to `stage:review` only after a `legal:approved` disposition is present.
A change labelled `legal:blocked` MUST NOT advance to code review or deployment.

#### Scenario: Legal stage is required for high-risk work
- GIVEN a change identified as having legal-risk triggers
- WHEN it completes security review
- THEN it is routed to `stage:legal` before code review
- AND `stage:review` is rejected until `legal:approved` is recorded

#### Scenario: Legal block prevents deployment
- GIVEN a pull request labelled `legal:blocked`
- WHEN `stage:deploy` is applied
- THEN the SDLC orchestrator fails the deployment gate
- AND the pull request remains blocked pending remediation or counsel sign-off