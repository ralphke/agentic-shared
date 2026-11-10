# Delta for personas

## ADDED Requirements

### Requirement: Bounded Persona Invocation Contract

Each orchestrated persona execution MUST receive the change identity, stage,
evaluated revision, planning content digest, and applicable Fabric skill
procedure. It MUST use the existing `.github/agents/` persona definition. A
duplicate orchestration-specific definition MUST NOT be required.

#### Scenario: Existing persona definitions are reused

- GIVEN the proposal stage is dispatched
- WHEN the execution starts
- THEN it uses the existing Product Owner persona definition and Fabric skill

### Requirement: Persona Execution Scope Restrictions

A persona execution MUST use only the tools and repository write paths allowed
for its stage. It MUST NOT receive gate-App, deployment, or protected-operation
credentials. It MUST NOT modify workflows, orchestration configuration, gate
policy, or source-of-truth specifications.

#### Scenario: Out-of-scope writes are rejected

- GIVEN a design-stage persona execution
- WHEN its output changes files outside the design stage's allowed paths
- THEN the output is not published
- AND the stage is reported as failed with the rejected paths

### Requirement: Verifiable Persona Completion

Each persona execution MUST return a structured result. The result MUST include
the outcome (`completed`, `needs-clarification`, `blocked`, or `failed`), the
outputs, any open questions, and the evaluated revision. The result is advisory.
Stage completion MUST be determined from independently verified outputs and
evidence.

#### Scenario: Self-reported success without verified output

- GIVEN a persona result that reports `completed`
- WHEN its required outputs fail validation or are absent
- THEN the stage is not advanced
- AND the failure reason is published

#### Scenario: Clarification request pauses the stage

- GIVEN a persona result that reports `needs-clarification` with questions
- WHEN the coordinator processes the result
- THEN the stage is blocked
- AND the questions are published for a human answer

### Requirement: Reviewer Persona Findings Are Not Approvals

Security, legal, and review personas MUST publish findings only. Their output
MUST NOT become a gate disposition or approval for their own work or for other
agents' work.

#### Scenario: Reviewer persona cannot approve

- GIVEN a security or code-review persona that reports no findings
- WHEN the coordinator evaluates the merge boundary
- THEN trusted gate evidence and independent human review are still required

### Requirement: All-Persona Runner Compatibility

The feasibility gate MUST record required tools, MCP bindings, dependencies,
and permissions for every persona, including adapter-owned handoffs. Every
CLI-dispatched persona MUST have a bounded runner execution with a transcript.
Missing required capabilities MUST block the gate; editor configuration MUST
NOT be assumed portable or silently omitted.

#### Scenario: An editor-only dependency blocks feasibility

- GIVEN a persona requires an MCP tool unavailable on the Actions runner
- WHEN the all-persona capability matrix is evaluated
- THEN the gate blocks with the missing binding and affected persona
- AND a Product Owner-only demonstration cannot clear it

#### Scenario: Supported runner bindings preserve persona responsibilities

- GIVEN every required capability has an exercised runner-compatible binding
- WHEN feasibility evidence is reviewed
- THEN every CLI-dispatched persona has a referenced bounded execution
- AND adapter-owned personas have verified handoff contracts
