# Design: Versioned Consumer Sync

## Decision

Use a repository-local `.agentic-shared.yml` manifest and a versioned release reference. Synchronization is performed by a workflow that creates a pull request in the consumer repository. The workflow is reviewable, rerunnable, and fails closed when it cannot prove that a managed file is safe to update.

## Manifest Contract

```yaml
source:
  repository: ralphke/agentic-shared
  version: v1.0.0

assets:
  agents: managed
  skills: extended
  prompts: extended
  instructions: extended
  workflows: managed
  issue_templates: extended
  specs: local

protected_paths:
  - .github/agents/local/**
  - .github/skills/local/**
  - spec/openspec/changes/**
```

Supported asset groups are `agents`, `skills`, `prompts`, `instructions`, `workflows`, `issue_templates`, and `specs`. Supported ownership modes are:

- `managed`: the shared release owns the selected paths; local edits require conflict resolution or promotion upstream.
- `extended`: shared files are synchronized, while consumer additions belong in reserved local directories.
- `local`: the consumer owns the asset group and no shared files are changed.

## File Layout

- `.agentic-shared.yml` — consumer configuration.
- `.github/skills/local/` — consumer-only skill extensions.
- `.github/agents/local/` — consumer-only agent extensions.
- `.github/prompts/local/` — consumer-only prompts.
- `.github/instructions/local/` — consumer-only instructions.
- `spec/openspec/changes/` — consumer-local change proposals.

## Sync Workflow

1. Check out the consumer repository and read `.agentic-shared.yml`.
2. Validate syntax, supported values, repository reference, and path safety.
3. Resolve the requested shared release or report that it is unavailable.
4. Compare the consumer's installed source version with the requested release.
5. Copy only paths allowed by the selected asset groups and exclude protected paths.
6. Detect local modifications to `managed` paths using the prior release as the comparison base.
7. Fail without writing files when a managed conflict is detected.
8. Create or update a branch and pull request containing the changes and validation summary.

The workflow must use a least-privilege token, must not push to the default branch, and must not modify protected local paths.

## Validation

The validator is a small, dependency-light script using the host's YAML parser where available. It must reject:

- missing `source.repository` or `source.version`;
- unsupported asset groups or ownership modes;
- absolute paths, parent traversal, or protected paths outside the repository;
- duplicate protected paths;
- malformed manifest values.

## Architecture Notes

### ADR-001: Release bundles instead of submodules

Git submodules expose source history but do not place `.github` assets naturally into the consumer repository and make local overlays awkward. Tagged release references plus pull requests provide explicit upgrades and normal consumer CI.

### ADR-002: Fail closed on managed conflicts

Overwriting a consumer's local changes would be more damaging than delaying an update. Conflicts must be reported for human resolution or promotion upstream.

### ADR-003: Separate shared and local extension paths

Separate `local/` directories make ownership visible, prevent accidental overwrite, and allow consumers to extend shared personas and skills without editing synchronized files.
