# Spec Delta

## Purpose

Provide a single revision-bound execution trace that lets participants inspect
Software Fabric activity and distinguish verified stage outcomes from missing,
failed, or self-reported evidence.

## ADDED Requirements

### Requirement: Stable trace identity

The system SHALL bind each trace to a unique ID, repository identity, explicit
resolved change directory, and implementation revision. It SHALL reject
ambiguous change selection and evidence from a different repository or revision.

#### Scenario: Same slug in different planning directories

- **WHEN** two change directories share a slug and the caller provides only that
  slug
- **THEN** initialization fails with a request for an explicit change directory
- **AND** no trace is created against a guessed directory

#### Scenario: Evidence from another revision

- **WHEN** a workflow result refers to an older head revision or another
  repository
- **THEN** the result is retained as mismatched evidence and does not satisfy
  the current stage

### Requirement: Distinct activity and outcome records

The system SHALL distinguish instruction discovery, instruction inclusion, skill
loading, agent invocation, command execution, and stage outcomes. Recording
activity SHALL NOT automatically mark a stage verified.

#### Scenario: Apply skill loaded without security invocation

- **WHEN** a session records loading the apply skill and reading the Fabric
  instructions
- **THEN** those activities appear in the trace
- **AND** the security stage remains missing until its required evidence is
  validated

### Requirement: Observed command execution

The system SHALL record start, completion, UTC time, exit code, invocation ID,
stage, and workspace revision for commands it executes. Nonzero exits,
interruptions, and uncommitted workspace changes SHALL remain visible and SHALL
NOT establish successful validation of a clean committed revision.

#### Scenario: Validation command fails

- **WHEN** a traced test command exits nonzero
- **THEN** its failure is recorded and propagated to the caller
- **AND** the test stage cannot be reported verified from that attempt

#### Scenario: Process stops before a completion event

- **WHEN** a trace contains a command start with no matching completion
- **THEN** the report marks the invocation unfinished rather than successful

### Requirement: Qualified provenance

The system SHALL classify evidence as collector-observed, provider-verified, or
self-reported. It SHALL revalidate referenced evidence before a readiness
decision. A manual event, arbitrary file, or unverified session import SHALL NOT
be upgraded to verified execution solely because it claims success.

#### Scenario: Fabricated success event

- **WHEN** a user imports an event asserting that all stages passed without
  verifiable evidence
- **THEN** the assertion remains self-reported and the overall trace is not
  verified complete

### Requirement: Complete stage inventory

Every report SHALL include proposal, design, implement, test, security, legal,
review, deploy, and operate, with separate activity and gate statuses. Gate
statuses SHALL distinguish missing, running, failed, unverified, stale,
verified, and not-applicable.

#### Scenario: No deployment configured

- **WHEN** proposal through review have sufficient evidence but deployment and
  operations have none
- **THEN** both missing stages appear in the report and prevent verified
  end-to-end completion

### Requirement: Explicit evidence contracts

The system SHALL evaluate each stage against a versioned evidence policy, not
labels or file existence. Contracts SHALL identify required evidence types and
trusted producers. An unconfigured contract or missing required evidence SHALL
fail closed with an actionable reason.

#### Scenario: Green test job masks failures

- **WHEN** a successful workflow lacks a required passing test report or
  measured coverage of at least 80 percent
- **THEN** the test gate is not verified
- **AND** the report names the absent or failing evidence

#### Scenario: Security or review evidence is insufficient

- **WHEN** security evidence contains HIGH or CRITICAL findings, omits required
  checks, or the current revision lacks an effective approval
- **THEN** the affected gate is not verified even if its stage label is present

### Requirement: Conditional legal review

The legal gate SHALL require an attributable, revision-bound risk assessment. A
low-risk assessment can establish not-applicable with accepted provenance. A
high-risk assessment SHALL require explicit clearance evidence before later
gates can yield verified end-to-end completion.

#### Scenario: No assessment recorded

- **WHEN** no risk assessment exists
- **THEN** legal is missing rather than automatically not-applicable

#### Scenario: High-risk assessment without clearance

- **WHEN** the assessment identifies a legal escalation trigger and clearance is
  absent
- **THEN** the legal gate remains incomplete and prevents verified end-to-end
  completion

### Requirement: Revision and dependency invalidation

The system SHALL invalidate affected gates when implementation content changes
and SHALL preserve earlier attempts. Planning evidence SHALL identify artifact
hashes and approval; deployment and operation evidence SHALL identify an
immutable deployed revision and its verified relationship to the reviewed
implementation.

#### Scenario: Push after successful tests

- **WHEN** the target implementation revision changes
- **THEN** previous tests, security results, and approvals cannot satisfy gates
  for the new revision without the contract's required revalidation

#### Scenario: Unrelated successful deployment

- **WHEN** a successful deployment targets a different artifact without verified
  lineage to the reviewed revision
- **THEN** deploy and operate remain unverified for this trace

### Requirement: Read-only GitHub collection

GitHub collection SHALL retrieve workflow attempts, job and step outcomes,
approvals, and deployment references using read-only access. It SHALL retain
source URLs and IDs, distinguish skipped or cancelled work from success, and
expose collection errors without substituting a passing result.

#### Scenario: Required job was skipped

- **WHEN** the run succeeded but the policy's required job or step was skipped
- **THEN** the corresponding gate is not verified

#### Scenario: API access denied

- **WHEN** GitHub evidence collection fails due to permissions or authentication
- **THEN** the command exits nonzero and the report identifies unavailable
  evidence
- **AND** a previously cached result is not silently treated as current

### Requirement: Durable consistent reporting

The system SHALL persist versioned trace events and produce JSON and Markdown
reports from the same validation result. Reports SHALL identify evidence,
provenance, target revision, stage failures, and next actions. Verified
end-to-end completion SHALL require all mandatory gates verified, with legal
verified or validly not-applicable, and valid prerequisite ordering.

#### Scenario: Report requested from an incomplete trace

- **WHEN** a participant generates a report containing a self-reported review
  and missing operations evidence
- **THEN** both output formats show the same incomplete result and source
  limitations
- **AND** the readiness command exits nonzero

#### Scenario: Full synthetic lifecycle

- **WHEN** deterministic fixtures provide valid evidence for every required
  stage and ordering constraint
- **THEN** both formats show evidence-complete with a simulation marker
- **AND** neither output claims that fixtures prove a real deployment occurred

### Requirement: Privacy-safe local storage

The system SHALL omit raw prompts, source bodies, credentials, command
environments, and stdout/stderr from default trace records. It SHALL reject
secret-bearing inputs in supported fields, redact credential-shaped values
before persistence, escape untrusted report text, and exclude runtime output
from version control by default.

#### Scenario: Command includes a credential

- **WHEN** a supported command field contains a credential-shaped value
- **THEN** the value is rejected or redacted before persistence
- **AND** the stored event and generated reports contain no such value

### Requirement: Opt-in integration and honest coverage

Tracing SHALL be explicitly enabled through a repo-local entry point without
editing managed shared assets. The trace SHALL disclose its observation boundary
and SHALL NOT claim to have captured host activity outside it. Plain OpenSpec
apply behavior SHALL remain unchanged.

#### Scenario: Skill invoked outside the trace wrapper

- **WHEN** a host invokes a skill without an observable trace event
- **THEN** the report does not invent an invocation
- **AND** it explains that uninstrumented activity is outside the trace's
  coverage
