"""Committed instruction contracts for non-overridable Fabric prerequisites."""

from pathlib import Path
import re
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ".github/instructions/openspec-workflow.instructions.md"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def normalized(content: str) -> str:
    return " ".join(content.split())


def skill_path(skill: str) -> tuple[str, ...]:
    return (f".github/skills/{skill}/SKILL.md",)


APPLY = skill_path("openspec-apply-change")
ARCHIVE = skill_path("openspec-archive-change")
BULK = skill_path("openspec-bulk-archive-change")
SYNC = skill_path("openspec-sync-specs")
VERIFY = skill_path("openspec-verify-change")
ONBOARD = skill_path("openspec-onboard")
PROPOSE = skill_path("openspec-propose")
FF = skill_path("openspec-ff-change")
CONTINUE = skill_path("openspec-continue-change")
EXPLORE = skill_path("openspec-explore")
NEW = skill_path("openspec-new-change")
INTAKE = (
    ".github/skills/idea-to-spec/SKILL.md",
    ".github/skills/software-fabric-kickoff/SKILL.md",
    ".github/agents/product-owner.agent.md",
)


class StrictOpenSpecPolicyTests(unittest.TestCase):
    def assert_contract(self, paths: tuple[str, ...], phrases: tuple[str, ...]) -> None:
        for path in paths:
            with self.subTest(path=path):
                content = normalized(read(path))
                for phrase in phrases:
                    self.assertIn(phrase, content)

    def test_capture_entry_points_offer_one_no_write_exit(self) -> None:
        self.assert_contract(PROPOSE + FF + NEW + ONBOARD + EXPLORE + INTAKE, (
            "Pre-Capture Intake Decision",
            WORKFLOW,
            "Proceed, Defer, or Do not pursue",
            "session storage",
            "Missing input pauses capture",
            "no repository writes",
            "deletion of existing work",
        ))

    def test_intake_exit_is_not_delivery_or_cleanup(self) -> None:
        self.assert_contract((WORKFLOW,), (
            "No delivery gates are needed merely to end intake",
            "no initialization, change directory, metadata, proposal, specs, design, tasks, or code",
            "not delivered or successfully archived",
            "Do not run archive or sync, mark tasks complete, or delete/revert existing work",
            "cleanup of an already captured proposal requires separate explicit authorization",
            "Missing input keeps capture paused",
            "do not ask the same decision again",
            "Proceed permits capture, not acceptance",
        ))
        self.assert_contract(PROPOSE + FF + NEW + ONBOARD + INTAKE, (
            "named repository artifacts counts as Proceed",
        ))
        self.assert_contract(("README.md",), (
            "before any repository capture write",
            "Defer or rejection needs no delivery gates",
            "It is not successful archive or task completion",
        ))

    def test_intake_boundary_precedes_scaffold_in_every_capture_path(self) -> None:
        for path in PROPOSE + FF + NEW + ONBOARD + EXPLORE:
            with self.subTest(path=path):
                content = read(path)
                self.assertLess(
                    content.index("Pre-Capture Intake Decision"),
                    content.index('openspec new change "'),
                )
        self.assert_contract(ONBOARD, (
            "Require explicit Proceed before Phase 4",
            "a generic acknowledgment is not capture consent",
        ))
        idea = read(INTAKE[0])
        self.assertLess(idea.index("**Load template and assess**"),
                        idea.index("**Pre-Capture Intake Decision**"))
        self.assertLess(idea.index("**Pre-Capture Intake Decision**"),
                        idea.index("**Capture after Proceed**"))
        kickoff = read(INTAKE[1])
        self.assertLess(kickoff.index("## Pre-Capture Intake Decision"),
                        kickoff.index("## Prerequisites"))

    def test_priority_and_issue_trigger_do_not_authorize_capture(self) -> None:
        self.assert_contract((".github/agents/product-owner.agent.md",), (
            "P0 never bypasses explicit Proceed",
            "If the requester is unavailable, keep capture paused",
        ))
        self.assert_contract((".github/workflows/sdlc-orchestrator.yml",), (
            "before any repository writes",
            "Missing input pauses capture",
            "not successful archive",
            "do not repeat that decision at handoff",
        ))
        self.assert_contract(skill_path("software-fabric-kickoff"), (
            "Stop after planning",
            "new explicit request",
            "Do not implement code during kickoff",
        ))

    def test_intake_handoffs_reuse_proceed_instead_of_prompting_again(self) -> None:
        self.assert_contract(PROPOSE + FF + NEW + ONBOARD + INTAKE, (
            "do not repeat",
        ))
        self.assert_contract(EXPLORE, (
            "explicit capture confirmation required by this skill counts as Proceed",
            "do not ask the same decision again",
        ))

    def test_central_contract_contains_all_existing_gates(self) -> None:
        self.assert_contract((WORKFLOW,), (
            "Missing or stale evidence blocks implementation.",
            "including the transitive dependencies of `applyRequires`",
            "`skip_specs` is not a waiver",
            "All new scenarios have passing tests",
            "No removed requirements are still referenced",
            "All CI checks are green",
            "no HIGH or CRITICAL findings",
            "New-code coverage is at least 80%",
            "At least one code-review approval",
            "All spec acceptance criteria are satisfied",
            "Required legal review is approved",
            "Applicable operational archive criteria",
            "User confirmation cannot override mandatory gates",
            "Local artifact validation does not certify external quality gates",
        ))

    def test_apply_requires_current_acceptance_before_code_edits(self) -> None:
        self.assert_contract(APPLY, (
            "Mandatory Planning Contract",
            "explicit acceptance of the current proposal/spec",
            "transitive `applyRequires`",
            "even when CLI state is `ready`",
            "Report the blocker and stop before code edits",
            "Genuinely optional artifacts remain warnings",
            "sourcePath",
            "line",
            "every delta is synced and verified",
        ))

    def test_archive_preflight_precedes_sync_and_cannot_be_confirmed_away(self) -> None:
        self.assert_contract(ARCHIVE + BULK, (
            "**Mandatory Fabric preflight:**",
            WORKFLOW,
            "Required artifacts/tasks and every mandatory gate must be complete and verifiable",
            "User confirmation cannot override mandatory gates",
            "Optional-artifact warnings remain informative",
            "Zero counts alone",
        ))
        for path in ARCHIVE + BULK:
            with self.subTest(path=path):
                content = read(path)
                self.assertLess(
                    content.index("Mandatory Fabric preflight"),
                    content.index("**Store selection:**"),
                )

    def test_single_archive_verifies_already_synced_deltas_too(self) -> None:
        self.assert_contract(ARCHIVE, (
            '"Sync and verify", "Cancel"',
            "verify every delta's content",
            "every delta has been synced and verified (including already-synced deltas)",
            "stop if the required specs role has no output",
            "do not claim rollback",
            "retire_capabilities: true",
            "RENAMED requirements present under the new name",
        ))

    def test_bulk_blocks_whole_changes_and_verifies_full_delta_list(self) -> None:
        self.assert_contract(BULK, (
            "Missing implementation evidence blocks the entire affected change",
            'Offer only "Archive N ready changes" and "Cancel"',
            "No delta may be excluded from an archived change",
            "**Verify every delta before moving changeRoot**",
            "only independent eligible changes may continue",
            "unresolved conflicts block affected changes",
            "Archive directory already exists",
            "Confirm the move did not nest",
            "Obtain all snapshots before the first write or move",
        ))

    def test_partial_direct_sync_is_not_an_archive_waiver(self) -> None:
        self.assert_contract(SYNC, (
            "Partial direct sync does not establish archive readiness",
            "must sync and verify every delta",
            "missing implementation blocks the entire affected change",
            "never widen it back to the full list",
        ))

    def test_verification_does_not_conflate_optional_omissions_with_mandatory_gates(self) -> None:
        self.assert_contract(VERIFY, (
            "User confirmation cannot override mandatory gates",
            "genuinely optional artifacts",
            "mandatory unverified checks block archive readiness",
            "report required task tracking as a blocker",
            "report a Fabric planning blocker",
            "Claim archive readiness only when every mandatory gate",
        ))

    def test_onboarding_uses_gated_apply_and_archive(self) -> None:
        self.assert_contract(ONBOARD, (
            "invoke `openspec-apply-change`",
            "explicit acceptance of the current proposal/spec",
            "Invoke `openspec-archive-change`",
            "user confirmation cannot override mandatory gates",
            "Sync and verify every delta before archive",
            "SHOW only after verified archive success",
        ))

    def test_planning_handoffs_require_acceptance_and_never_waive_required_roles(self) -> None:
        self.assert_contract(PROPOSE + FF, (
            "obtain acceptance before design",
            "mandatory Fabric proposal, specs, design, and task roles",
            "do not treat it as satisfied",
            "Skip only genuinely optional artifacts",
            "Accept the current proposal/spec before requesting apply",
        ))
        self.assert_contract(CONTINUE, (
            "Obtain proposal acceptance before design",
            "a skipped required role blocks readiness",
            "explicit acceptance of the current proposal/spec",
            "every-delta sync verification",
        ))
        self.assert_contract(EXPLORE, (
            "Proposal acceptance precedes design",
            "cannot be waived by conditional guidance or skipped statuses",
            "Never write a blocked artifact to bypass a required prerequisite",
            "explicit acceptance of the current proposal/spec",
        ))

    def test_known_generated_body_bypasses_are_absent(self) -> None:
        patterns = (
            r"archive without syncing",
            r"proceed if user confirms",
            r"don't block archive on warnings",
            r"archived with \d+ incomplete",
            r"before all artifacts are done \(if tasks exist\)",
            r"jump to implementation \(if tasks exist\)",
            r"excludedDeltas|includedDeltas",
            r"skip spec sync only when implementation is missing",
            r"dependencies are enablers, not gates",
            r"spec-driven's `design\.md` qualifies",
            r"skip_specs: true.*report the spec-dependent checks as not applicable",
            r"ready for archive \(with noted improvements\)",
            r"openspec archive .+ --yes",
        )
        for path in APPLY + ARCHIVE + BULK + SYNC + VERIFY + ONBOARD + PROPOSE + FF + CONTINUE + EXPLORE:
            content = normalized(read(path))
            for pattern in patterns:
                with self.subTest(path=path, pattern=pattern):
                    self.assertIsNone(re.search(pattern, content, re.I))

    def test_personas_and_design_stage_preserve_stage_gates(self) -> None:
        self.assert_contract((
            ".github/agents/developer.agent.md",
            ".github/agents/openspec.agent.md",
        ), ("explicit acceptance of the current proposal/spec",))
        self.assert_contract((
            ".github/agents/operations-sre.agent.md",
        ), ("Quality Gate Checklist", "Every delta synced and verified",))
        content = read(".github/workflows/sdlc-orchestrator.yml")
        design_stage = content.split("'## 🏗️ Stage: Design'", 1)[1].split(
            "'Expected outputs:'", 1
        )[0]
        self.assertIn("spec-to-design skill after proposal acceptance", design_stage)
        self.assertNotIn("openspec-apply-change", design_stage)
        yaml.safe_load(content)
        config = yaml.safe_load(read("openspec/config.yaml"))
        self.assertIn(
            "user confirmation cannot override mandatory gates",
            " ".join(config["operations"]["archive"]["guidance"]),
        )

    def test_readme_distinguishes_restoration_and_external_gate_evidence(self) -> None:
        self.assert_contract(("README.md",), (
            "User confirmation cannot override mandatory gates",
            "Restoration does not rewrite generated bodies",
            "green run is not complete Software Fabric archive clearance",
            "Genuinely optional artifacts",
        ))


if __name__ == "__main__":
    unittest.main()
