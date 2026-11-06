# Tasks

## 1. UX Brief Skill and Agent Integration

- [x] 1.1 Add `.github/skills/ux-design/SKILL.md` with the brief workflow,
  inputs, output structure, quality checks, and clarification/stop conditions;
  verify the skill includes the shared purpose, trigger, steps, checks, and
  expected-output sections.
- [x] 1.2 Update `.github/agents/ux-designer.agent.md` to use the skill and
  retain its role boundaries; extend
  `tests/test_ux_designer_stage.py` for the agent-skill contract and key
  requirements, then run `python -m pytest -q tests/test_ux_designer_stage.py`.

## 2. Quality Evidence and Validation

- [x] 2.1 Record a lightweight before-and-after assessment in
  `doc/ux-designer-skill-assessment.md`, comparing clarity, structure,
  execution guidance, and handoff quality with cited examples; run Markdown
  lint on the assessment and changed guidance files.
- [x] 2.2 Run `openspec validate strengthen-ux-designer-brief-workflow --strict`
  and the focused UX persona tests; resolve any validation failures before
  reporting the change ready for review.
