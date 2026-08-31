# Tasks: Migrate Prompt Entry Points to OpenSpec Skills

## Skill implementation

- [x] 1. Add `openspec-propose`, `openspec-apply-change`, and `openspec-verify-change`
  `SKILL.md` assets using current upstream OpenSpec conventions and Software Fabric gates.
- [x] 2. Add the `software-fabric-kickoff` skill with an explicit approval boundary before
  it delegates to apply or verification.
- [x] 3. Add a shared Node.js 26+ and OpenSpec CLI prerequisite guard to every command
  skill, including clear install and initialization guidance with no prompt fallback.

## Consumer transition and documentation

- [x] 4. Update README, shared instructions, and consumer guidance with replacement skill
  names, Node.js 26+ setup, `openspec init`, root verification, and prompt deprecation schedule.
- [x] 5. Update the shared asset manifest and sync behavior only as necessary to publish
  replacement skills while preserving `prompts: local` and protected local prompt paths.
- [x] 6. Mark shared prompt wrappers as deprecated for one compatibility release; do not
  remove them in this change.

## Tests and validation

- [x] 7. Add deterministic tests for front matter, command mapping, prerequisite failure,
  planning-only proposal behavior, and kickoff approval boundary.
- [x] 8. Extend synchronization tests for replacement skills and preservation of local
  prompt extensions across the transition.
- [x] 9. Run the focused Python tests, manifest validation, and repository checks; record
  results and complete acceptance criteria.
- [x] 10. Validate GitHub `idea` issue intake and direct `/opsx:propose` entry paths,
  including the orchestrator guidance and proposal-skill contract.