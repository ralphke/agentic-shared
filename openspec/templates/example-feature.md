# Example OpenSPEC Change: Add CSV Export

This example shows a minimal compliant change set.

---

## Example proposal (`openspec/changes/add-csv-export/proposal.md`)

# Proposal: Add CSV Export

**Change Slug:** `add-csv-export`  
**Author:** Product Owner  
**Date:** 2026-06-05  
**Status:** Draft  
**Priority:** P2

## Intent
Users need a downloadable CSV export for filtered table results. Today they copy data manually, which is slow and error-prone.

## Scope
- [ ] Add authenticated CSV export endpoint.
- [ ] Add export action in the table UI.
- [ ] Add audit log entry for each export.

## Out of Scope
- Scheduled exports.
- PDF export.

## Approach
Add one API endpoint and reuse existing query filters so exported data matches what users see in the UI.

## Scenarios
### Scenario: Export succeeds for authenticated user
- GIVEN an authenticated user with filtered results
- WHEN the user requests CSV export
- THEN the system returns a CSV file containing only those filtered records

### Scenario: Export denied for unauthenticated user
- GIVEN no valid authentication
- WHEN CSV export is requested
- THEN the system returns `401 Unauthorized`

### Scenario: Empty results export
- GIVEN valid authentication and zero filtered results
- WHEN CSV export is requested
- THEN the system returns an empty CSV with headers only

## Acceptance Criteria
- [ ] Authenticated users can export filtered data to CSV.
- [ ] Unauthenticated export requests return `401`.
- [ ] Empty result sets export with headers and no data rows.

## Affected Domains
- `idea-capture`
- `testing-standards`

---

## Example delta spec (`openspec/changes/add-csv-export/specs/testing-standards/spec.md`)

# Delta for testing-standards

## ADDED Requirements

### Requirement: CSV Export Regression Coverage
The test suite MUST validate CSV export authorization, success, and empty-result behavior.

#### Scenario: Authorized export test exists
- GIVEN a change introducing CSV export
- WHEN tests execute in CI
- THEN at least one integration test validates successful export for authenticated users

#### Scenario: Unauthorized export test exists
- GIVEN a change introducing CSV export
- WHEN tests execute in CI
- THEN at least one integration test validates `401 Unauthorized` for unauthenticated requests

## MODIFIED Requirements

### Requirement: Scenario-to-test traceability
All new proposal scenarios MUST be represented by at least one automated test.
(Previously: Important scenarios SHOULD be represented by tests.)

#### Scenario: Proposal scenario mapping is complete
- GIVEN a proposal with three scenarios
- WHEN the QA stage completes
- THEN tests map to all three scenarios

## REMOVED Requirements

### Requirement: Manual export verification only
(Removed because: export behavior is now validated automatically in CI.)
