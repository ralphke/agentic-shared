# Tasks

## 1. Operations SRE Skill Associations

- [ ] 1.1 Add an `Associated Skills` section to
      `.github/agents/operations-sre.agent.md` that names
      `workflow-retrospective` and `openspec-archive-change`, gives each a
      task-specific use condition, and preserves the archive gates; verify the
      section matches both skill descriptions and makes no exclusivity claim.

## 2. Validation

- [ ] 2.1 Run
      `openspec validate --change "declare-operations-sre-skill-mapping" --strict`
      and `git diff --check`; resolve any reported issues before handoff.
