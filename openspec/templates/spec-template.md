# OpenSPEC Delta Spec Template

Use this template for:

`openspec/changes/<slug>/specs/<domain>/spec.md`

---

# Delta for <domain>

## ADDED Requirements

### Requirement: <new requirement name>
<Use MUST/SHALL/SHOULD language.>

#### Scenario: <scenario name>
- GIVEN <precondition>
- WHEN <action>
- THEN <expected outcome>

## MODIFIED Requirements

### Requirement: <existing requirement name>
<Updated requirement text.>
(Previously: <short summary of prior behavior>)

#### Scenario: <scenario name>
- GIVEN <precondition>
- WHEN <action>
- THEN <expected outcome>

## REMOVED Requirements

### Requirement: <removed requirement name>
(Removed because: <reason>)

---

## Authoring Rules

- Include at least one scenario for each ADDED or MODIFIED requirement.
- Keep requirements testable and unambiguous.
- Prefer small, focused deltas over broad unrelated edits.
