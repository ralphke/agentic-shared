from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_ux_designer_persona_defines_accessibility_and_responsive_brief():
    persona = (ROOT / ".github/agents/ux-designer.agent.md").read_text()

    assert "github_pr_label: stage:ux" in persona
    assert "ux-brief.md" in persona
    assert "WCAG 2.2 AA" in persona
    assert "desktop, tablet, and mobile" in persona
    assert "keyboard" in persona
    assert "touch" in persona
    assert "TypeScript" in persona
    assert "Rayfin" in persona


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
    assert "label the handoff PR `stage:ux`" in product_owner
    assert "Read `ux-brief.md` before design" in architect
    assert "`ux-brief.md` is the" in developer
    assert "UX acceptance criteria in `ux-brief.md`" in qa


def test_sdlc_workflow_gates_ux_before_design_and_requires_the_brief():
    workflow = (ROOT / ".github/workflows/sdlc-orchestrator.yml").read_text()

    ux_gate_start = workflow.index("stage-ux-gate:")
    design_gate_start = workflow.index("stage-design-gate:")
    ux_gate = workflow[ux_gate_start:design_gate_start]
    design_gate = workflow[design_gate_start:]

    assert "github.event.label.name == 'stage:ux'" in ux_gate
    assert "stage:ux requires a change folder" in ux_gate
    assert 'if [ ! -f "$dir/proposal.md" ]; then' in ux_gate
    assert "Create `openspec/changes/<slug>/ux-brief.md`" in ux_gate
    assert "Pass the completed brief to the Architect" in ux_gate
    assert 'if [ ! -f "$dir/ux-brief.md" ]; then' in design_gate
    assert "Missing UX handoff artifact. Expected ux-brief.md" in design_gate
    assert workflow.index("5. 🧪 Tests (QA Engineer)") < workflow.index(
        "6. 🔒 Security Review (Security Engineer)"
    )
