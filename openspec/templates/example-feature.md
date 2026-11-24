# Example OpenSPEC Change: Add CSV Export

This example shows a minimal compliant change set.

---

## Example proposal (`openspec/changes/add-csv-export/proposal.md`)

### Why

Users need a downloadable CSV export for filtered table results. Today they copy
data manually, which is slow and error-prone.

### Scope

- Add an authenticated CSV export endpoint.
- Add an export action in the table UI.
- Add an audit log entry for each export.

### Out of Scope

- Scheduled exports.
- PDF export.

### What Changes

- Add CSV export to filtered table results.
- Reuse existing filters so exported data matches the visible result set.
- Record each export in the existing audit stream.

### Capabilities

#### New Capabilities

None.

#### Modified Capabilities

- `testing-standards`: add CSV export authorization, success, and empty-result
  regression coverage.

### UX Applicability

```json
{
  "required": true,
  "reason": "The accepted scope adds an export action to the filtered table interface."
}
```

### Build / Buy / Vibe

Build within the existing application because export, filtering, and audit
controls are already available there.

### Legal / IP Notes

CSV export exposes only data already available to the authenticated user. No
additional regulated-data, licensing, or intellectual-property trigger is
identified.

### Scenarios

#### Scenario: Export succeeds for authenticated user

- GIVEN an authenticated user with filtered results
- WHEN the user requests CSV export
- THEN the system returns a CSV file containing only those filtered records

#### Scenario: Export denied for unauthenticated user

- GIVEN no valid authentication
- WHEN CSV export is requested
- THEN the system returns `401 Unauthorized`

#### Scenario: Empty results export

- GIVEN valid authentication and zero filtered results
- WHEN CSV export is requested
- THEN the system returns an empty CSV with headers only

### Acceptance Criteria

- [ ] Authenticated users can export filtered data to CSV.
- [ ] Unauthenticated export requests return `401`.
- [ ] Empty result sets export with headers and no data rows.

### Impact

- Updates the export API, table UI, audit integration, and scenario-driven tests.
- Requires no new dependency or infrastructure service.

---

## Example delta spec (`openspec/changes/add-csv-export/specs/testing-standards/spec.md`)

### Delta for testing-standards

#### ADDED Requirements

##### Requirement: CSV Export Regression Coverage

The test suite MUST validate CSV export authorization, success, and empty-result
behavior.

###### Scenario: Authorized export test exists

- GIVEN a change introducing CSV export
- WHEN tests execute in CI
- THEN at least one integration test validates successful export for
  authenticated users

###### Scenario: Unauthorized export test exists

- GIVEN a change introducing CSV export
- WHEN tests execute in CI
- THEN at least one integration test validates `401 Unauthorized` for
  unauthenticated requests

#### MODIFIED Requirements

##### Requirement: Scenario-to-test traceability

All new proposal scenarios MUST be represented by at least one automated test.
(Previously: Important scenarios SHOULD be represented by tests.)

###### Scenario: Proposal scenario mapping is complete

- GIVEN a proposal with three scenarios
- WHEN the QA stage completes
- THEN tests map to all three scenarios

#### REMOVED Requirements

##### Requirement: Manual export verification only

(Removed because: export behavior is now validated automatically in CI.)
