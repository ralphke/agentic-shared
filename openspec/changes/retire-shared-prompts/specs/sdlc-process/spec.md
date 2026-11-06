# Delta for sdlc-process

## ADDED Requirements

### Requirement: Shared OpenSpec Workflows Use Command Skills

The repository MUST publish shared OpenSpec workflow entry points only as
maintained command skills that invoke the OpenSpec CLI. It MUST NOT publish
shared `.prompt.md` wrappers for those workflows. Consumer-owned prompts under
`.github/prompts/local/**` MUST remain outside this retirement.

#### Scenario: Shared workflow entry points use command skills

- **GIVEN** a consumer adopts the shared workflow assets
- **WHEN** it starts an OpenSpec workflow
- **THEN** the shared entry point is a maintained command skill
- **AND** the skill uses the OpenSpec CLI

#### Scenario: Synchronization retires shared prompt wrappers

- **GIVEN** a consumer synchronizes a release that retires shared wrappers
- **WHEN** an unchanged shared prompt wrapper is no longer present upstream
- **THEN** synchronization removes that unchanged shared wrapper
- **AND** the corresponding maintained command skill remains available

#### Scenario: Consumer-local prompts are preserved

- **GIVEN** a consumer has prompt files under `.github/prompts/local/**`
- **WHEN** it synchronizes the release that retires shared wrappers
- **THEN** the consumer-local prompt files remain untouched

#### Scenario: OpenSpec CLI is unavailable

- **GIVEN** a user invokes a shared command skill without a working OpenSpec CLI
- **WHEN** the skill checks its prerequisites
- **THEN** it reports the prerequisite and stops without changing artifacts
- **AND** it does not fall back to a shared prompt wrapper
