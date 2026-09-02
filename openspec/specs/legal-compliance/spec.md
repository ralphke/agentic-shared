# Legal Compliance - Source of Truth

> **Domain:** `legal-compliance` | **Owner:** legal-compliance  
> Defines legal and compliance review requirements for licensing, use rights,
> intellectual property, regulated data, and mandatory escalation in the
> Software Fabric lifecycle.

---

## Purpose

Defines the legal and compliance checks required for changes involving data, rights, licensing, or regulatory risk.

## Overview

Legal and compliance review identifies obligations and unresolved risk; it does
not replace qualified legal counsel. A change MUST not proceed to code review,
deployment, or operation when it has unresolved high-risk legal, regulatory,
licensing, or rights concerns.

---

## Requirements

### Requirement: Legal Review Scope
Each change requiring legal review MUST document its target audience,
jurisdictions, deployment and distribution model, affected data categories, and
third-party components, content, models, datasets, APIs, or services.

#### Scenario: Review scope identifies applicable concerns
- GIVEN a proposed feature intended for commercial distribution in two regions
- WHEN the Legal & Compliance Agent starts its review
- THEN the review records the target regions and distribution model
- AND it identifies applicable data, licensing, consumer, and IP concerns

#### Scenario: Insufficient scope prevents approval
- GIVEN a proposal with no identified deployment model or target audience
- WHEN the Legal & Compliance Agent evaluates the proposal
- THEN the decision is `HUMAN REVIEW REQUIRED` or `CONDITIONAL`
- AND the missing information is recorded as required remediation

---

### Requirement: Rights and License Verification
Every third-party dependency, asset, dataset, model, API, or service introduced
by a change MUST have documented provenance and terms that permit the intended
use, distribution, and deployment model. Required attribution, notice, source
disclosure, and commercial-use obligations MUST be captured before release.

#### Scenario: Compatible dependency is approved with obligations recorded
- GIVEN a change that adds a third-party library with known license terms
- WHEN the Legal & Compliance Agent verifies the library against the intended use
- THEN the review records the library, license, and compatibility result
- AND any required notices or attribution are listed as release obligations

#### Scenario: Unclear use rights block release
- GIVEN a change that includes a dataset with unclear redistribution rights
- WHEN the Legal & Compliance Agent reviews its provenance and terms
- THEN the change is marked `BLOCK` or `HUMAN REVIEW REQUIRED`
- AND release does not proceed until the rights ambiguity is resolved

---

### Requirement: Regulated and Personal Data Assessment
Changes that collect, process, store, share, transfer, or infer personal,
sensitive, health, financial, or otherwise regulated data MUST identify the
data categories, processing purpose, retention and deletion expectations,
sharing boundaries, and applicable obligations.

#### Scenario: Personal data requires legal escalation
- GIVEN a change that processes customer contact information
- WHEN the Legal & Compliance Agent assesses the affected data
- THEN the change requires human legal review before release
- AND the assessment records privacy, retention, and sharing obligations

#### Scenario: No regulated data is in scope
- GIVEN a change limited to synthetic test data with no identifying attributes
- WHEN the Legal & Compliance Agent completes the data assessment
- THEN the review records that no regulated data is handled
- AND the decision may proceed based on the remaining review criteria

---

### Requirement: Intellectual Property and AI Risk Assessment
Changes using third-party, adapted, or AI-generated code, content, models, or
data MUST assess ownership, provider terms, reuse restrictions, attribution,
and material copyright, trademark, patent, trade-secret, or database-right
risks relevant to the intended use.

#### Scenario: AI-generated content is reviewed for intended use
- GIVEN a change that incorporates AI-generated product documentation
- WHEN the Legal & Compliance Agent reviews the change
- THEN the assessment records the model provider terms and intended distribution
- AND it identifies any required review, attribution, or content restrictions

#### Scenario: Unresolved ownership claim requires escalation
- GIVEN a proposed asset with a disputed or unknown owner
- WHEN the Legal & Compliance Agent evaluates the asset
- THEN the decision is `BLOCK` or `HUMAN REVIEW REQUIRED`
- AND the asset is not released until ownership or permission is established

---

### Requirement: Risk Decision and Evidence
Each legal review MUST produce an auditable assessment with a decision of
`APPROVE`, `CONDITIONAL`, `BLOCK`, or `HUMAN REVIEW REQUIRED`; an overall risk
rating of `LOW`, `MEDIUM`, or `HIGH`; the evidence considered; and any required
remediation or escalation owner.

#### Scenario: Conditional approval tracks required remediation
- GIVEN a change whose dependency license requires attribution
- WHEN the Legal & Compliance Agent issues a conditional decision
- THEN the assessment identifies the attribution requirement and accountable owner
- AND the change remains in legal review until the requirement is verified

#### Scenario: Approval contains sufficient audit evidence
- GIVEN a low-risk internal change with all relevant rights and obligations verified
- WHEN the Legal & Compliance Agent approves the change
- THEN the assessment records the reviewer, date, decision, risk rating, and evidence
- AND the PR may advance to the code review stage

---

### Requirement: Mandatory Human Legal Sign-Off
Human legal counsel MUST review a change before approval when it involves
regulated or personal data, external commercial distribution, substantial
third-party code or content redistribution, ambiguous or restrictive rights,
novel AI or data licensing exposure, or a material risk of regulatory penalties
or rights-holder dispute.

#### Scenario: High-risk change cannot bypass legal review
- GIVEN a proposal involving personal data and external commercial distribution
- WHEN the Software Fabric lifecycle evaluates its gates
- THEN the change is assigned the `stage:legal` review gate
- AND it cannot advance to review or deployment until human legal sign-off is recorded

#### Scenario: Resolved escalation allows progress
- GIVEN a change previously marked `HUMAN REVIEW REQUIRED`
- WHEN qualified legal counsel records an approved disposition and conditions
- THEN the Legal & Compliance Agent updates the assessment with that evidence
- AND the change may progress only after all stated conditions are complete

---

### Requirement: Legal Gate Handoff
The Legal & Compliance Agent MUST post the assessment on the relevant issue or
pull request and communicate the decision to the next responsible role. An
approved legal assessment MUST be represented by the `legal:approved` pull
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