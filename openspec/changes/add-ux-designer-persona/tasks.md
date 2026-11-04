# Tasks

## 1. Persona and UX handoff

- [x] 1.1 Add `.github/agents/ux-designer.agent.md` with the `stage:ux` trigger,
  UX brief requirements, accessibility and responsive checks, and Architect
  handoff; verify it passes Markdown lint.
- [x] 1.2 Update the Product Owner, Architect, Developer, and QA handoffs,
  shared persona roster, and OpenSpec persona roster; verify all references
  point to the UX brief and `stage:ux`.
- [x] 1.3 Add focused tests for the UX persona and roster contract; verify them
  with `python3 -m pytest -q tests/test_ux_designer_stage.py`.

## 2. Workflow stage gate

- [ ] 2.1 Add the `stage:ux` orchestrator gate and require `ux-brief.md` in the
  existing design gate; verify the UX handoff and missing-brief rejection are
  covered by the focused workflow tests.
- [ ] 2.2 Extend the focused workflow tests to assert the `stage:ux` trigger,
  proposal validation, UX brief handoff, and design-gate requirement; verify
  them with `python3 -m pytest -q tests/test_ux_designer_stage.py`.

## 3. Integration validation

- [ ] 3.1 Validate the change with `openspec validate
  --change add-ux-designer-persona --strict` and run the focused tests and
  tracked Markdown lint; resolve all findings before handoff.
