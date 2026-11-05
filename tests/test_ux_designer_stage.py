from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


def test_ux_designer_persona_defines_accessibility_and_responsive_brief():
    persona = " ".join(
        (ROOT / ".github/agents/ux-designer.agent.md").read_text().split()
    )

    assert "github_pr_label: stage:ux" in persona
    assert "ux-brief.md" in persona
    assert "WCAG 2.2 AA" in persona
    assert "desktop, tablet, and mobile" in persona
    assert "keyboard" in persona
    assert "touch" in persona
    assert "TypeScript" not in persona
    assert "Rayfin" not in persona
    assert "Do not select, prescribe, or propose a replacement stack" in persona
    assert (
        "flag it to the Systems Architect with evidence and user-impact rationale"
        in persona
    )
    assert "no UX stage, brief, UX-specific specs, or UX tests" in persona
    assert "without creating UX artifacts" in persona


def test_ux_design_skill_defines_evidence_based_brief_process():
    persona = (ROOT / ".github/agents/ux-designer.agent.md").read_text()
    skill = " ".join(
        (ROOT / ".github/skills/ux-design/SKILL.md").read_text().split()
    )

    assert ".github/skills/ux-design/SKILL.md" in persona

    for section in (
        "## When to Use This Skill",
        "## Execution Steps",
        "## `ux-brief.md` Structure",
        "## Quality Checks",
        "## Stop Conditions",
        "## Handoff",
    ):
        assert section in skill

    for requirement in (
        "accepted proposal",
        "assumptions and unknowns",
        "loading, empty, validation, success, failure",
        "WCAG 2.2 AA",
        "desktop, tablet, and mobile",
        "Given/When/Then",
        "QA chooses the validation method",
        "do not select or recommend a replacement stack",
    ):
        assert requirement in skill


def test_persona_rosters_and_downstream_handoffs_reference_ux():
    instructions = (ROOT / ".github/instructions/sdlc-fabric.instructions.md").read_text()
    config = (ROOT / "openspec/config.yaml").read_text()
    product_owner = (ROOT / ".github/agents/product-owner.agent.md").read_text()
    architect = (ROOT / ".github/agents/architect.agent.md").read_text()
    developer = (ROOT / ".github/agents/developer.agent.md").read_text()
    qa = (ROOT / ".github/agents/qa-engineer.agent.md").read_text()

    assert "ux-designer.agent.md" in instructions
    assert "`stage:ux`" in instructions
    assert "ux-designer=.github/agents/ux-designer.agent.md" in config
    assert "label the handoff PR `stage:ux` for visual" in product_owner
    assert "Read `ux-brief.md` before design" in architect
    assert "platform, language, framework" in architect
    assert "build/test instructions needed" in architect
    assert "stack selection to UX or the Developer" in architect
    assert "`ux-brief.md` is the" in developer
    assert "specified by the Architect in `design.md`" in developer
    assert "infer or choose the product stack from UX suggestions" in developer
    assert "UX acceptance criteria in `ux-brief.md`" in qa

    persona_spec = (
        ROOT
        / "openspec/specs/personas/spec.md"
    ).read_text()
    assert "UX Designer flags an obsolete or infeasible technology" in persona_spec
    assert "Architect Provides an Implementation-Ready Technology Handoff" in persona_spec


def test_nonvisual_personas_require_no_ux_artifacts_but_preserve_functional_gates():
    for name in ("product-owner", "ux-designer", "architect", "developer", "qa-engineer"):
        persona = " ".join(
            (ROOT / f".github/agents/{name}.agent.md").read_text().split()
        )
        assert "UX Applicability" in persona, name
        assert "CLI-only, API-only, and framework changes" in persona, name
        assert "require no UX stage, brief, UX-specific specs, or UX tests" in persona, name
        assert "functional" in persona, name


def test_planning_and_qa_skills_use_the_conditional_ux_contract():
    for name in (
        "idea-to-spec", "ux-design", "spec-to-design", "test-generation",
        "software-fabric-kickoff",
    ):
        skill = " ".join(
            (ROOT / f".github/skills/{name}/SKILL.md").read_text().split()
        )
        assert "UX Applicability" in skill, name
        assert "CLI-only, API-only, and framework" in skill, name
        assert "no UX" in skill, name
    qa = (ROOT / ".github/skills/test-generation/SKILL.md").read_text()
    assert "every stable UX criterion ID" in qa
    assert "Unavailable required checks remain blocked" in qa


def test_sdlc_workflow_uses_conditional_ux_gate_and_rechecks_updated_prs():
    workflow = (ROOT / ".github/workflows/sdlc-orchestrator.yml").read_text()

    ux_gate_start = workflow.index("stage-ux-gate:")
    design_gate_start = workflow.index("stage-design-gate:")
    ux_gate = workflow[ux_gate_start:design_gate_start]
    design_gate = workflow[design_gate_start:]

    assert "github.event.label.name == 'stage:ux'" in ux_gate
    assert "--phase ux" in ux_gate
    assert "For visual changes only" in ux_gate
    assert "create no UX artifacts or UX tests" in ux_gate
    assert "--phase design" in design_gate
    assert "--phase test" in design_gate
    assert "synchronize" in workflow
    assert "github.event.pull_request.labels.*.name" in workflow
    assert workflow.index("5. 🧪 Tests (QA Engineer)") < workflow.index(
        "6. 🔒 Security Review (Security Engineer)"
    )


def test_canonical_specs_preserve_all_selected_ux_requirements_and_scenarios():
    for change in (
        "add-ux-designer-persona",
        "strengthen-ux-designer-brief-workflow",
        "conditional-ux-stage-and-validation",
    ):
        for delta_path in (ROOT / "openspec/changes" / change / "specs").glob("*/spec.md"):
            canonical = (
                ROOT / "openspec/specs" / delta_path.parent.name / "spec.md"
            ).read_text()
            delta = delta_path.read_text()
            requirements = re.split(r"^### Requirement: ", canonical, flags=re.MULTILINE)
            canonical_blocks = {
                block.splitlines()[0]: block for block in requirements[1:]
            }
            for block in re.split(
                r"^### Requirement: ", delta, flags=re.MULTILINE
            )[1:]:
                name = block.splitlines()[0]
                assert name in canonical_blocks, (change, name)
                scenarios = re.findall(r"^#### Scenario: (.+)$", block, re.MULTILINE)
                for scenario in scenarios:
                    assert f"#### Scenario: {scenario}" in canonical_blocks[name], (
                        change, name, scenario
                    )
            assert not re.search(
                r"^## (ADDED|MODIFIED|REMOVED|RENAMED) Requirements",
                canonical,
                re.MULTILINE,
            )


def test_canonical_specs_define_conditional_routing_and_independent_quality_gates():
    personas = " ".join(
        (ROOT / "openspec/specs/personas/spec.md").read_text().split()
    )
    process = " ".join(
        (ROOT / "openspec/specs/sdlc-process/spec.md").read_text().split()
    )
    testing = " ".join(
        (ROOT / "openspec/specs/testing-standards/spec.md").read_text().split()
    )
    assert "**ten SDLC-stage personas**" in personas
    assert "UX Designer (for visual changes)" in personas
    assert "no UX artifact, UX test, or frontend tooling is required" in personas
    assert "nonvisual changes MUST route directly to architecture" in process
    assert "Applicability MUST be checked separately for each change" in process
    assert "X -- No, no UX artifacts --> D" in process
    assert "legal:approved" in process
    assert "Code coverage ≥ 80% on new code" in process
    assert "No HIGH or CRITICAL vulnerabilities" in process
    assert "Nonvisual Changes Have No UX Testing Obligations" in testing
    assert "emulation is distinguished from real-device validation" in testing
    assert "Configured consumer UX automation MUST pass" in testing
    assert "New code MUST achieve ≥ 80% line coverage" in testing
