# Delta for sdlc-process

## ADDED Requirements

### Requirement: Executable Stage Orchestration

When enabled, the Software Fabric orchestrator MUST execute the applicable
stage persona through a single selected, supported execution mechanism. Each
dispatch MUST be traceable to the change, stage, persona, evaluated revision,
and execution reference. Handoff comments, mentions, and label changes MUST
NOT count as stage execution.

#### Scenario: Accepted work executes the existing stage personas

- GIVEN authorized intake and a configured execution mechanism
- WHEN the coordinator starts a Fabric change
- THEN the Product Owner persona executes the existing proposal procedure
- AND later applicable personas execute only after their prerequisites and
  approval boundaries pass
- AND every execution and handoff records a verifiable execution reference

#### Scenario: Comment-only handoff cannot complete a stage

- GIVEN a stage for which no execution reference exists
- WHEN a handoff comment, mention, or stage label is added
- THEN the stage remains incomplete
- AND the published status names the missing execution

#### Scenario: Orchestration disabled or unconfigured is visible

- GIVEN orchestration is disabled or its execution credential is missing
- WHEN an eligible Fabric event arrives
- THEN the coordinator reports a blocked status with the setup action
- AND no stage is reported as succeeded

### Requirement: Verified Stage Advancement

A stage MUST advance only after the coordinator independently verifies the
stage outputs and applicable gates. The executing agent's own report MUST NOT be
sufficient.

#### Scenario: Unverified output does not advance

- GIVEN a stage execution reports success
- WHEN its required outputs or applicable gates are not verified
- THEN the stage does not advance and the reason is published

### Requirement: Ordered Human Approvals

The orchestrator MUST require explicit Proceed before capture and proposal
acceptance before UX or design. Before implementation is dispatched, it MUST
also require acceptance of the current complete proposal, specs, design, and
tasks, plus explicit implementation authorization. Labels, agent output,
OpenSpec CLI readiness, and task checkboxes MUST NOT count as approval.

#### Scenario: Design waits for proposal acceptance

- GIVEN a captured proposal without explicit acceptance
- WHEN a stage label or agent result indicates design readiness
- THEN no design persona is dispatched and the missing acceptance is published

### Requirement: Content-Bound Approval Validity

Each approval MUST come from an authorized human's explicit action, not an
agent-generated claim. It MUST be bound to the content digest and revision reviewed. A
change to that content MUST invalidate dependent approvals.

#### Scenario: Missing acceptance or changed planning blocks implementation

- GIVEN planning artifacts are ready
- AND current proposal/spec acceptance or implementation authorization is
  missing or bound to different content
- WHEN an event requests implementation
- THEN no implementation agent is dispatched
- AND the coordinator names the required approval and affected content

#### Scenario: Unauthorized or agent-generated approval is rejected

- GIVEN an approval command or review from an actor without write permission,
  or a claimed approval supplied by agent output
- WHEN the coordinator evaluates approvals
- THEN the approval is ignored and the rejection reason is published

### Requirement: Single-Maintainer Planning Authorization

One authorized human MAY provide all ordered planning approvals, including
for work they initiated, and MAY own the execution's Copilot credential.
No separate automation account SHALL be required. Agent execution MUST remain
isolated from repository write and protected-operation credentials.
Single-maintainer planning MUST be reported as reduced assurance and MUST NOT
replace independent review or any existing delivery gate.

#### Scenario: One human approves planning using their own Copilot credential

- GIVEN a human with write permission who also owns the Copilot credential
- WHEN that human supplies the ordered content-bound approvals
- THEN planning approvals are valid without a second planning approver
- AND status reports reduced assurance while delivery gates remain unchanged

#### Scenario: Credential reuse does not make agent output approval

- GIVEN an agent authenticates with the planning approver's Copilot credential
- WHEN the agent claims that planning is approved
- THEN the claim cannot substitute for the human's explicit approval
- AND execution has no repository write or protected-operation credential

### Requirement: Maintainer-Only Fabric Delivery Initiation

Merge-triggered Fabric delivery MUST verify the merged PR, base branch, exact
merge revision, and API-reported merger against a configured human actor ID.
Fabric manual starts and reruns MUST also verify the initiating human.
Unauthorized or ambiguous initiation MUST block before privileged work.
Ordinary PR CI MUST remain automatic.

#### Scenario: Only the configured maintainer's merge initiates delivery

- GIVEN the configured delivery actor is the numeric GitHub user ID of ralphke
- WHEN a merged PR is resolved through authenticated GitHub API data
- THEN delivery qualifies only for that actor's merge to the expected base
- AND another user's merge, a bot merge, or an ambiguous mapping blocks

#### Scenario: A different user cannot rerun an authorized delivery

- GIVEN a workflow originally initiated by the configured maintainer
- WHEN another user manually dispatches or reruns Fabric orchestration
- THEN current initiator verification blocks privileged work
- AND the original actor does not authorize the new invocation

### Requirement: Authorized Delivery Continuation Provenance

Automated Fabric delivery continuations MUST trace verified workflow/run
provenance to an authorized merge and its exact revision. Reusable workflows
and adapters MUST enforce the same authorization at their entry points before
privileged work. A generic successful workflow or bot identity MUST NOT confer
authorization.

#### Scenario: Automated continuation retains the authorized merge boundary

- GIVEN a verified maintainer-authorized merge and an expected adapter run
- WHEN its completion triggers the next delivery stage
- THEN that stage verifies originating run provenance and revision
- AND a forged completion, changed target, or direct unauthorized call blocks

### Requirement: External Revision Adoption

An external branch update MUST pause dispatch and supersede in-flight results.
Publication MUST use an expected-SHA ref update without overwriting external
work. Resumption MUST require authorized adoption of the exact current head,
artifact revalidation, and fresh revision-bound approvals. Adoption MUST NOT
itself accept planning or authorize implementation.

#### Scenario: Copilot or human changes the automation branch

- GIVEN a running persona and a branch update outside verified publication
- WHEN the result is processed
- THEN its patch is not published and further dispatch pauses
- AND the status requests review and adoption of the external head

#### Scenario: Adoption does not preserve stale approval

- GIVEN an authorized adoption command naming the current full head SHA
- WHEN the coordinator revalidates the change
- THEN stale approvals and results remain invalid
- AND changed planning requires renewed acceptance before implementation

#### Scenario: Branch moves during publication or adoption

- GIVEN the branch head no longer matches the expected SHA
- WHEN publication or adoption is attempted
- THEN no external commit is overwritten and the change remains blocked

### Requirement: Fabric Intake Routing and Stage Labels

Eligible Fabric work without a stage label MUST be assigned `stage:proposal`.
Conflicting stage labels MUST be reported for human review, and the earliest
stage remains authoritative. Task-router intake MUST enter Fabric proposal
intake. It MUST NOT request or assign implementation directly. An explicit
standalone OpenSpec selection MUST be reported as outside Fabric orchestration
and MUST NOT bypass repository controls.

#### Scenario: Task-router request cannot authorize implementation

- GIVEN an issue labeled for Copilot or containing a Copilot request
- WHEN the task router processes it
- THEN the issue is routed to Fabric intake with the next required action
- AND no implementation request or assignment is made

#### Scenario: Unlabeled and conflicting stage labels

- GIVEN one eligible Fabric PR with no stage label and another with two stage
  labels
- WHEN the coordinator processes them
- THEN the first receives `stage:proposal`
- AND the second is flagged for review with the earliest stage authoritative

### Requirement: Conditional Stage Routing and Bounded Rework

The orchestrator MUST route the UX stage only when the accepted proposal's UX
applicability is `required: true`. It MUST route the legal stage when an owning
persona flags a high-risk trigger. If either decision is missing or conflicting,
handoff MUST block. Failed test, security, legal, or review outcomes MUST route
back to the owning earlier stage within a configured rework limit. When that
limit is reached, the change MUST block for a human decision.

#### Scenario: Nonvisual change skips UX and high-risk change requires legal

- GIVEN an accepted nonvisual proposal that a persona flags as legally high-risk
- WHEN the coordinator plans the stage route
- THEN UX is not dispatched
- AND legal review is required before review or deployment

#### Scenario: Rework limit exhausted blocks the change

- GIVEN a change whose review has failed the configured maximum number of times
- WHEN review fails again
- THEN no further implementation is dispatched
- AND the change is blocked for a maintainer decision

### Requirement: Idempotent, Resumable Orchestration

The orchestrator MUST derive lifecycle state from authoritative evidence each
time it runs. It MUST NOT dispatch the same stage twice for the same change,
revision, and attempt. Results produced for a stale revision MUST NOT advance
the current revision. The orchestrator MUST support cancellation and bounded
retries. It MUST resume from durable prior work after workflow or agent
interruption.

#### Scenario: Duplicate or delayed events do not repeat stage work

- GIVEN a stage is running or has completed for a specific change revision
- WHEN duplicate, concurrent, or out-of-order events arrive
- THEN the coordinator reconciles existing state without a duplicate dispatch
- AND stale results cannot advance the current revision

#### Scenario: Failed or unavailable execution remains visible

- GIVEN an agent fails, times out, requests clarification, or lacks credentials
- WHEN its stage result is processed
- THEN the change reports failed or blocked with a concrete next action
- AND it does not advance through a success-shaped fallback
- AND authorized recovery respects the retry limit and prior work

#### Scenario: Cancellation stops in-flight work

- GIVEN a dispatched stage execution
- WHEN an authorized maintainer cancels the change
- THEN in-flight executions are cancelled and no later stage is dispatched

### Requirement: Protected Delivery Boundaries

Merge, release, and archive MUST pass only through the existing trusted Fabric
gate controls. When protected operations are disabled, or when required trusted
evidence is absent, the orchestrator MUST report the blocked boundary. It MUST
NOT merge, publish, deploy, or archive through any other route. Archive MUST
require complete delta verification and fresh archive evidence before sync or
move.

#### Scenario: Disabled protected operations cannot complete delivery

- GIVEN merge/release controls are disabled or required evidence is absent
- WHEN pre-delivery work finishes
- THEN the coordinator reports the blocked boundary
- AND it does not merge, publish, deploy, or archive through another route
