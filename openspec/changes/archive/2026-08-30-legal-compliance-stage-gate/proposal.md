# Proposal: Add Legal Compliance Stage Gate

> **Change slug:** `legal-compliance-stage-gate`  
> **Priority:** P1  
> **Affected domains:** `sdlc-process`, `legal-compliance`  
> **Created:** 2026-08-30

---

## Intent

The Software Fabric declares legal review as a conditional high-risk gate, but
the GitHub Actions orchestrator currently routes security directly to code
review. This makes the legal review label advisory and permits legal-review
work to bypass the documented handoff.

Add an explicit `legal:approved` disposition label and an orchestrator stage
for `stage:legal`. The orchestrator will block review and deployment when work
in legal review is blocked or lacks the approved disposition.

---

## Scope

- [ ] Add a `stage:legal` orchestrator handoff job.
- [ ] Require `legal:approved` before legally routed work can enter review or deployment.
- [ ] Block review and deployment for `legal:blocked` work.
- [ ] Align legal-review instructions and SDLC delta requirements with the gate.
- [ ] Validate the workflow YAML and OpenSpec artifacts.

---

## Out of Scope

- Automatic classification of high-risk changes.
- Replacing qualified human legal counsel.
- Creating or configuring GitHub repository labels or branch-protection rules.

---

## Scenarios

### Scenario: Legal review starts
- GIVEN a pull request labelled `stage:legal`
- WHEN the SDLC orchestrator receives the label event
- THEN it posts the legal-review handoff and required disposition labels

### Scenario: Approved legal review enters code review
- GIVEN a pull request labelled `stage:legal` and `legal:approved`
- WHEN `stage:review` is applied
- THEN the review-stage gate succeeds

### Scenario: Undisposed legal review is blocked
- GIVEN a pull request labelled `stage:legal` without `legal:approved`
- WHEN `stage:review` or `stage:deploy` is applied
- THEN the stage gate fails with instructions to record a legal disposition

### Scenario: Blocked legal review cannot deploy
- GIVEN a pull request labelled `legal:blocked`
- WHEN `stage:deploy` is applied
- THEN the deployment-stage gate fails

---

## Acceptance Criteria

- [ ] The orchestrator has a job triggered by `stage:legal`.
- [ ] `stage:review` fails for work in legal review without `legal:approved`.
- [ ] `stage:review` and `stage:deploy` fail when `legal:blocked` is present.
- [ ] Legal-review instructions direct approved work to apply `legal:approved`.
- [ ] The OpenSpec structure validation includes the `legal-compliance` domain.
