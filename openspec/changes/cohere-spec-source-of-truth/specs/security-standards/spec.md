# Delta for security-standards

## MODIFIED Requirements

### Requirement: Devcontainer validation may record a scoped security warning

The devcontainer image validation lane MAY override a blocking HIGH or CRITICAL
image finding only for that validation lane. The override MUST produce a strict
warning rather than a passed result and MUST record the affected finding,
justification, security reviewer, remediation owner, expiry or renewal point,
and mandatory follow-up. The override MUST NOT apply to application code,
deployment, merge, release, or archive security gates.

#### Scenario: Devcontainer validation records an approved warning

- GIVEN a HIGH or CRITICAL finding affects only a devcontainer image
  dependency used for local development validation
- WHEN an identified security reviewer approves the narrowly scoped
  exception
- THEN the validation result is recorded as
  `security:devcontainer-warning`
- AND it names the finding, justification, reviewer, remediation owner, and
  expiry or renewal point
- AND a linked mandatory follow-up issue or task is created

#### Scenario: Devcontainer warning cannot satisfy a production gate

- GIVEN a devcontainer security warning exists for the current revision
- WHEN an application, merge, release, deployment, or archive security gate
  is evaluated
- THEN the warning is not treated as passed security evidence
- AND any applicable HIGH or CRITICAL finding still blocks that gate

#### Scenario: Exception expires without remediation

- GIVEN a devcontainer warning reaches its expiry or renewal point
- WHEN remediation has not been completed and verified
- THEN the devcontainer exception is no longer valid
- AND the validation lane returns to a blocking result until renewed with
  current evidence

#### Scenario: Warning lacks accountable follow-up

- GIVEN a devcontainer override request has no remediation owner, expiry,
  or linked follow-up
- WHEN the request is reviewed
- THEN the override is rejected
- AND the original HIGH or CRITICAL finding remains blocking
