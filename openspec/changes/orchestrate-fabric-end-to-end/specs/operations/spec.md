# Delta for operations

## ADDED Requirements

### Requirement: Configured Deployment and Operations Adapters

Post-merge deployment and operations stages MUST run only through adapters
declared in consumer configuration. Their outcome evidence MUST come from
trusted sources and MUST be bound to the merged or deployed revision. A missing
adapter, a failed adapter run, or absent operational evidence MUST block the
applicable completion. The orchestrator MUST NOT invent deployment targets,
SLOs, or exemptions.

#### Scenario: Configured deployment and operations finish the lifecycle

- GIVEN required reviews and protected merge/release conditions pass
- WHEN authorized consumer adapters complete deployment and operations
- THEN their evidence binds the deployed revision and applicable stability gates
- AND complete delta verification and fresh archive evidence precede sync or
  move
- AND absent adapters or operational evidence block applicable completion

#### Scenario: Missing adapter blocks deployment

- GIVEN a merged change and no configured deployment adapter
- WHEN the deploy stage is evaluated
- THEN the change is blocked with the missing-adapter setup action

### Requirement: Orchestration Status Visibility

Every eligible orchestration event MUST publish its route, change, current
stage, status, and next action or blocker. When execution was dispatched, it
MUST also publish the execution reference. Status MUST be published on the
linked issue or PR and in the run summary. Ineligible events MUST record why
they were ignored. Published status describes progress and MUST NOT serve as
approval or gate evidence.

#### Scenario: Every eligible event reports status

- GIVEN an eligible event for a Fabric change
- WHEN the coordinator finishes processing it
- THEN the status shows route, stage, status, any execution reference, and next
  action
- AND no eligible event finishes as a silent skip

### Requirement: Orchestration Administration and Rollback

Shared guidance MUST document the orchestration prerequisites, including
repository plan, execution credential, permissions, credential separation,
installation, and consumer configuration. It MUST also document limits,
consumer ownership of local stores and extensions, upstream skill ownership,
and rollback by disabling orchestration. Orchestration MUST be disabled by
default and MUST NOT enable protected operations.

#### Scenario: Rollback restores manual Fabric operation

- GIVEN orchestration is enabled for a consumer
- WHEN a maintainer disables it in configuration
- THEN no new persona executions are dispatched
- AND the existing manual Fabric skills and gates remain usable

### Requirement: Shared Agent Prerequisite Setup

Cloud-agent setup and CLI execution MUST reuse one shared prerequisite setup
action with the Fabric-supported OpenSpec pin. The cloud setup job contract
MUST remain intact. Privileged jobs MUST resolve setup from the trusted base,
not PR content. Shared setup MUST NOT expose execution, gate, or deployment
credentials merely to install prerequisites.

#### Scenario: Both execution contexts use consistent prerequisites

- GIVEN cloud-agent setup and CLI execution use the shared setup action
- WHEN their prerequisite checks run
- THEN both verify the supported Node.js baseline and OpenSpec version
- AND the cloud-specific setup job remains discoverable

#### Scenario: PR setup changes cannot execute with privileged credentials

- GIVEN a PR changes the shared setup action
- WHEN a privileged orchestration job runs
- THEN it resolves setup from the trusted base SHA instead

### Requirement: Per-Change Execution Budgets

Before dispatch, the coordinator MUST reserve an attempt and its full timeout
against configured per-change dispatch and execution-time limits. Failed,
cancelled, and superseded attempts MUST count. Missing or unverifiable
accounting MUST block dispatch. Retry and adoption MUST NOT reset or bypass
budgets; increases require reviewed trusted configuration.

#### Scenario: Retry cannot bypass an exhausted budget

- GIVEN failed and cancelled attempts have consumed a change's budget
- WHEN an authorized retry is requested
- THEN no persona is dispatched and the exhausted limit is reported

#### Scenario: Concurrent or interrupted work remains accounted

- GIVEN an active reservation or an interrupted run with unknown duration
- WHEN another dispatch is evaluated
- THEN the full outstanding reservation counts against the limits
- AND a reservation exceeding either limit blocks dispatch

### Requirement: Transparent Cost Estimates

Enabled execution MUST require a dated owner-supplied per-dispatch charge
estimate, currency, and billing assumptions. Status MUST report usage,
reservations, and estimated next-run and remaining charges separately from
enforced execution limits. Estimates MUST NOT be presented as actual billing
or a guaranteed monetary spending cap.

#### Scenario: Missing pricing assumptions block execution

- GIVEN charge assumptions are missing from an enabled configuration
- WHEN dispatch is evaluated
- THEN it blocks with configuration guidance instead of assuming free usage

#### Scenario: Status distinguishes estimates from provider charges

- GIVEN valid dated billing assumptions and reconstructed usage
- WHEN status is published
- THEN it shows consumed and reserved usage and next-run and remaining estimates
- AND it identifies the estimate source and separate provider billing controls

### Requirement: Consumer Delivery Actor Configuration

Consumer configuration MUST explicitly identify the human authorized to initiate
Fabric delivery by numeric GitHub user ID. Missing configuration MUST block
delivery. Guidance MUST distinguish workflow authorization from repository-wide
merge permissions and administrator powers. The maintainer's own Copilot
credential MUST be supported without requiring another account.

#### Scenario: Consumers configure their own maintainer

- GIVEN a consumer has not configured its authorized delivery actor
- WHEN merge-triggered Fabric delivery is evaluated
- THEN delivery blocks with setup guidance
- AND the shared assets do not implicitly authorize the upstream maintainer
