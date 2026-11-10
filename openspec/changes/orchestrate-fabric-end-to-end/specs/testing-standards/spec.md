# Delta for testing-standards

## ADDED Requirements

### Requirement: Orchestration Transition and Recovery Tests

The shared orchestration MUST have deterministic automated tests that run
without network access or live credentials. These tests MUST cover every
lifecycle transition, approval boundary and invalidation, conditional UX and
legal route, event-ordering case, recovery path, and disabled configuration.

#### Scenario: Boundary tests run in CI without credentials

- GIVEN the shared script test workflow
- WHEN it runs on a pull request
- THEN orchestration transition, approval, idempotency, and recovery tests
  execute with fixture data and no live agent or GitHub credentials

### Requirement: Orchestration Evidence Spoofing Tests

Automated tests MUST show that labels, agent self-reports, task checkboxes, and
generic or untrusted check names cannot replace trusted gate evidence.

#### Scenario: Spoofed evidence is rejected

- GIVEN fixture events with a matching stage label, a successful agent result,
  and a check named like a gate check but from an untrusted source
- WHEN the coordinator evaluates the merge boundary
- THEN the boundary remains blocked

### Requirement: Isolated End-to-End Orchestration Demonstration

Before production use is recommended, an authorized and isolated demonstration
MUST record actual stage executions through the selected mechanism. Each
execution record MUST include its execution reference and must cover at least
one negative path, such as missing authorization or a rejected write. The
demonstration MUST clearly distinguish fixture or dry-run validation from
actual agent execution. Neither form of validation grants production clearance.

#### Scenario: Demonstration records actual and negative executions

- GIVEN an authorized isolated demonstration change
- WHEN the orchestrator runs it
- THEN the record lists each actual stage execution with its reference
- AND it includes a blocked negative path
- AND it states that the demonstration is not production clearance

### Requirement: Coexistence and Budget Regression Tests

Deterministic tests MUST cover single-maintainer credential reuse, external
revision adoption, racing branch updates, stale approval rejection, and budget
reservation across retries and interrupted runs. Workflow contracts MUST
verify shared setup reuse and trusted-base resolution. The feasibility record
MUST include all-persona runner compatibility evidence.

#### Scenario: Revisions are covered without live service access

- GIVEN fixture identities, external commits, and execution accounting
- WHEN shared script tests run without credentials
- THEN credential reuse, adoption, race, stale-approval, and budget cases are exercised
- AND setup contracts verify both entry points and trusted-base resolution

### Requirement: Delivery Initiator Authorization Tests

Tests MUST cover the configured maintainer's merge, another user's merge,
bot/auto-merge, wrong base or revision, ambiguous PR lookup, unauthorized manual
dispatch and rerun, and invalid continuation provenance. Workflow contracts
MUST verify authorization precedes privileged jobs and applies to reusable
entry points. Ordinary PR CI MUST remain unaffected.

#### Scenario: An original authorized actor cannot conceal a rerun initiator

- GIVEN a fixture with the maintainer as original actor and another rerun actor
- WHEN Fabric authorization tests run
- THEN privileged work is rejected
- AND valid maintainer and verified continuation fixtures pass authorization
- AND fixture PR CI still runs without the delivery actor restriction
