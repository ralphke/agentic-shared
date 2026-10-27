# Spec Delta

## ADDED Requirements

### Requirement: Operations SRE Agent Skills MUST Be Explicitly Associated

The Operations SRE Agent instructions SHALL name the skills intended for its
responsibilities and state when to use each, without claiming exclusive access
or runtime enforcement.

#### Scenario: Retrospective work selects its skill

- **GIVEN** the Operations SRE Agent is asked to review recurring SDLC process
  friction
- **WHEN** it selects a skill for the task
- **THEN** its instructions identify `workflow-retrospective` for that work.

#### Scenario: Archival selects its skill after operational gates

- **GIVEN** the Operations SRE Agent has verified the required operational
  stability and archive gates
- **WHEN** it proceeds to archive a completed change
- **THEN** its instructions identify `openspec-archive-change` for that work.

#### Scenario: Skill association does not imply exclusivity

- **GIVEN** another agent or user invokes one of the named skills
- **WHEN** skill discovery or invocation occurs
- **THEN** the Operations SRE Agent mapping does not represent that invocation
  as prohibited or runtime-blocked.
