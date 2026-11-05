"""Fixtures for conditional UX artifact and workflow gates."""

from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import shlex

import yaml


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / ".github/skills/test-generation/scripts/validate_ux_gate.py"
SPEC = importlib.util.spec_from_file_location("validate_ux_gate", SCRIPT)
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


class UXFixture(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve() / "changes"
        self.change = self.root / "example"
        self.change.mkdir(parents=True)

    def proposal(self, required=False, reason="API-only; no affected visual interface"):
        self.write("proposal.md", "## UX Applicability\n\n```json\n"
                   + json.dumps({"required": required, "reason": reason}) + "\n```\n")

    def write(self, name, text):
        (self.change / name).write_text(text, encoding="utf-8")

    def brief(self):
        self.write("ux-brief.md", "# Brief\n### UX-01: Error is actionable\n"
                   "- Given a failed request\n- When shown\n- Then explain recovery\n")


class UXGateTests(UXFixture):
    def test_nonvisual_cli_and_api_real_cli_need_no_ux_artifacts(self):
        for reason in ("CLI-only command", "API-only framework"):
            self.proposal(reason=reason)
            for phase in ("ux", "design", "test", "complete", "security"):
                result = subprocess.run(
                    [sys.executable, str(SCRIPT), str(self.change),
                     "--root", str(self.root), "--phase", phase],
                    capture_output=True, text=True,
                    env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("no UX artifacts or tests required", result.stdout)
            self.assertEqual([p.name for p in self.change.iterdir()], ["proposal.md"])

    def test_visual_brief_is_required_after_ux_and_can_pass(self):
        self.proposal(True)
        with redirect_stdout(io.StringIO()):
            self.assertTrue(gate.validate_change(self.change, self.root, "ux"))
            with self.assertRaises(FileNotFoundError):
                gate.validate_change(self.change, self.root, "design")
            self.brief()
            self.assertTrue(gate.validate_change(self.change, self.root, "design"))

    def test_missing_duplicate_invalid_or_conflicting_decision_fails(self):
        for value in ("false", None, 0, [], {}):
            self.proposal(value)
            with self.subTest(value=value), self.assertRaises(gate.UXGateError):
                gate.applicability(self.change)
        self.proposal(reason=" ")
        with self.assertRaises(gate.UXGateError):
            gate.applicability(self.change)
        for text in (
            "# Missing section\n",
            "## UX Applicability\n```json\n"
            '{"required":false,"required":true,"reason":"conflicting"}\n```\n',
            "## UX Applicability\n```json\n{}\n```\n" * 2,
            "## UX Applicability\n```json\n{broken}\n```\n",
        ):
            self.write("proposal.md", text)
            with self.subTest(text=text), self.assertRaises(ValueError):
                gate.applicability(self.change)

    def test_fenced_example_cannot_supply_a_real_decision_or_criterion(self):
        self.write("proposal.md", "````markdown\n## UX Applicability\n"
                   '```json\n{"required":false,"reason":"example"}\n```\n````\n')
        with self.assertRaises(gate.UXGateError):
            gate.applicability(self.change)
        self.write("ux-brief.md", "```markdown\n### UX-01: Example only\n```\n")
        with self.assertRaises(gate.UXGateError):
            gate.brief_criteria(self.change)

    def test_empty_artifacts_and_duplicate_brief_criteria_fail(self):
        self.write("proposal.md", " \n")
        with self.assertRaisesRegex(gate.UXGateError, "empty required artifact"):
            gate.applicability(self.change)
        self.brief()
        with (self.change / "ux-brief.md").open("a", encoding="utf-8") as brief:
            brief.write("### UX-01: Duplicate outcome\n")
        with self.assertRaisesRegex(gate.UXGateError, "unique"):
            gate.brief_criteria(self.change)

    def test_outside_change_paths_and_read_failures_are_explicit(self):
        with self.assertRaises(gate.UXGateError):
            gate.validate_change(self.root.parent, self.root, "design")
        self.proposal()
        error = io.StringIO()
        with patch("sys.argv", ["gate", str(self.change), "--root", str(self.root),
                                "--phase", "design"]):
            with patch.object(Path, "read_text", side_effect=PermissionError("read denied")):
                with redirect_stderr(error):
                    self.assertEqual(gate.main(), 1)
        self.assertIn("read denied", error.getvalue())

    def test_artifact_resolving_outside_change_is_rejected(self):
        original_resolve = Path.resolve
        def resolve(path, *args, **kwargs):
            if path.name == "proposal.md":
                return self.root.parent / "outside.md"
            return original_resolve(path, *args, **kwargs)
        with patch.object(Path, "resolve", resolve), self.assertRaises(gate.UXGateError):
            gate.artifact(self.change.resolve(), "proposal.md")

    def report(self, **overrides):
        entry = {
            "id": "UX-01", "method": "automated", "result": "passed",
            "evidence": "https://example.test/ci/run/123",
        }
        entry.update(overrides)
        self.write("ux-validation.json", json.dumps({"criteria": [entry]}))

    def test_visual_report_requires_complete_passing_criterion_mapping(self):
        self.proposal(True)
        self.brief()
        self.report()
        with redirect_stdout(io.StringIO()):
            self.assertTrue(gate.validate_change(self.change, self.root, "complete"))
        for overrides in (
            {"id": "UX-02"}, {"result": "failed"}, {"result": "blocked"},
            {"method": "guess"}, {"evidence": ""}, {"evidence": None},
        ):
            self.report(**overrides)
            with self.subTest(overrides=overrides), self.assertRaises(gate.UXGateError):
                gate.validate_report(self.change.resolve(), {"UX-01"})
        for text in ('{"criteria":[]}', '{"criteria":{}}', "{broken}"):
            self.write("ux-validation.json", text)
            with self.subTest(text=text), self.assertRaises(ValueError):
                gate.validate_report(self.change.resolve(), {"UX-01"})
        self.report()
        report = json.loads((self.change / "ux-validation.json").read_text())
        report["criteria"] *= 2
        self.write("ux-validation.json", json.dumps(report))
        with self.assertRaises(gate.UXGateError):
            gate.validate_report(self.change.resolve(), {"UX-01"})
        (self.change / "ux-validation.json").unlink()
        with self.assertRaises(FileNotFoundError):
            gate.validate_report(self.change.resolve(), {"UX-01"})

    def check_run(self, **overrides):
        result = {
            "name": "Browser UX", "head_sha": "a" * 40,
            "status": "completed", "conclusion": "success",
        }
        result.update(overrides)
        return result

    def test_automation_cannot_be_replaced_by_stale_failed_or_ambiguous_checks(self):
        gate.evaluate_checks([self.check_run()], ["Browser UX"], "a" * 40)
        for run in (
            self.check_run(head_sha="b" * 40), self.check_run(conclusion="failure"),
            self.check_run(conclusion="skipped"), self.check_run(conclusion="cancelled"),
        ):
            with self.subTest(run=run), self.assertRaises(gate.UXGateError):
                gate.evaluate_checks([run], ["Browser UX"], "a" * 40)
        with self.assertRaises(gate.UXGateError):
            gate.evaluate_checks([self.check_run()] * 2, ["Browser UX"], "a" * 40)
        for runs in ([], [self.check_run(status="in_progress")]):
            with self.assertRaises(gate.PendingChecks):
                gate.evaluate_checks(runs, ["Browser UX"], "a" * 40)

    def test_invalid_visual_check_configuration_is_rejected(self):
        for text in ("", "[]", '[""]', '["x","x"]', "[1]", '["Stage: Security"]'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                gate.configured_checks(text)

    def test_waiting_is_bounded_and_rereads_results(self):
        with patch.object(gate, "fetch_checks", return_value=[]):
            with self.assertRaisesRegex(gate.UXGateError, "timed out"):
                gate.wait_for_checks("owner/repo", "a" * 40, ["Browser UX"], timeout=0)
        with patch.object(gate, "fetch_checks", side_effect=[[], [self.check_run()]]):
            with patch.object(gate.time, "sleep") as sleep, redirect_stdout(io.StringIO()):
                gate.wait_for_checks("owner/repo", "a" * 40, ["Browser UX"])
        sleep.assert_called_once()

    def test_nonvisual_main_never_reads_check_configuration_or_calls_github(self):
        self.proposal()
        with patch("sys.argv", ["gate", str(self.change), "--root", str(self.root),
                                "--phase", "security"]):
            with patch.object(gate, "configured_checks") as config:
                with patch.object(gate, "fetch_checks") as fetch:
                    with redirect_stdout(io.StringIO()):
                        self.assertEqual(gate.main(), 0)
        config.assert_not_called()
        fetch.assert_not_called()

    def test_visual_main_requires_current_head_automation_after_report(self):
        self.proposal(True)
        self.brief()
        self.report()
        with patch("sys.argv", [
            "gate", str(self.change), "--root", str(self.root),
            "--phase", "complete", "--head", "a" * 40, "--repository", "owner/repo",
        ]):
            with patch.dict(os.environ, {"UX_CHECK_NAMES": '["Browser UX"]'}):
                with patch.object(gate, "fetch_checks", return_value=[self.check_run()]) as fetch:
                    with redirect_stdout(io.StringIO()):
                        self.assertEqual(gate.main(), 0)
                fetch.assert_called_once_with("owner/repo", "a" * 40)
                with patch.object(gate, "fetch_checks",
                                  return_value=[self.check_run(conclusion="failure")]):
                    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                        self.assertEqual(gate.main(), 1)

    def test_paginated_check_results_and_command_errors_are_not_silently_ignored(self):
        response = subprocess.CompletedProcess(
            [], 0, stdout=json.dumps([
                {"check_runs": []}, {"check_runs": [self.check_run()]},
            ]),
        )
        with patch.object(gate.subprocess, "run", return_value=response):
            self.assertEqual(gate.fetch_checks("owner/repo", "a" * 40), [self.check_run()])
        for value in ({}, [{}], [{"check_runs": None}]):
            response.stdout = json.dumps(value)
            with patch.object(gate.subprocess, "run", return_value=response):
                with self.assertRaises(gate.UXGateError):
                    gate.fetch_checks("owner/repo", "a" * 40)

    def test_diff_discovery_excludes_archived_and_removed_but_requires_active_changes(self):
        root = Path("openspec/changes")
        response = subprocess.CompletedProcess(
            [], 0, stdout=(
                "openspec/changes/example/proposal.md\0"
                "openspec/changes/example/tasks.md\0"
                "openspec/changes/archive/old/proposal.md\0"
                "openspec/changes/removed/proposal.md\0"
                "README.md\0"
            ),
        )
        with patch.object(gate.subprocess, "run", return_value=response):
            with patch.object(Path, "is_dir", lambda path: path.name == "example"):
                with redirect_stdout(io.StringIO()) as output:
                    changes = gate.changed_changes(root, "a" * 40, "b" * 40)
        self.assertEqual(changes, [root / "example"])
        self.assertIn("removed change excluded", output.getvalue())
        response.stdout = "openspec/changes/archive/old/proposal.md\0"
        with patch.object(gate.subprocess, "run", return_value=response):
            with self.assertRaisesRegex(gate.UXGateError, "no active change"):
                gate.changed_changes(root, "a" * 40, "b" * 40)
            with self.assertRaisesRegex(gate.UXGateError, "repository-relative"):
                gate.changed_changes(self.root, "a" * 40, "b" * 40)
        with self.assertRaisesRegex(gate.UXGateError, "full commit SHAs"):
            gate.changed_changes(root, "main", "b" * 40)

    def test_main_reports_command_failures_and_missing_revision_arguments(self):
        with patch("sys.argv", [
            "gate", "--phase", "design", "--base", "a" * 40, "--head", "b" * 40,
        ]):
            with patch.object(gate.subprocess, "run", side_effect=(
                subprocess.CalledProcessError(1, ["git"], stderr="diff denied")
            )):
                with redirect_stderr(io.StringIO()) as error:
                    self.assertEqual(gate.main(), 1)
        self.assertIn("diff denied", error.getvalue())
        with patch("sys.argv", ["gate", "--phase", "design"]):
            with redirect_stderr(io.StringIO()) as error:
                self.assertEqual(gate.main(), 1)
        self.assertIn("provide change directories or both", error.getvalue())


class UXWorkflowTests(UXFixture):
    def setUp(self):
        super().setUp()
        self.repo = self.root.parent
        self.root.rename(self.repo / "openspec-changes")
        self.root = self.repo / "openspec" / "changes"
        self.root.parent.mkdir()
        (self.repo / "openspec-changes").rename(self.root)
        self.change = self.root / "example"
        self.workflow = yaml.safe_load(
            (ROOT / ".github/workflows/sdlc-orchestrator.yml").read_text(encoding="utf-8")
        )
        self.git("init", "--quiet")
        self.git("config", "user.email", "fixture@example.test")
        self.git("config", "user.name", "Fixture")
        self.git("commit", "--allow-empty", "--quiet", "-m", "base")
        self.base = self.git("rev-parse", "HEAD")

    def git(self, *args):
        return subprocess.run(
            ["git", "-C", str(self.repo), *args],
            check=True, capture_output=True, text=True,
        ).stdout.strip()

    def run_step(self, job, name):
        self.git("add", ".")
        self.git("commit", "--allow-empty", "--quiet", "-m", "change")
        head = self.git("rev-parse", "HEAD")
        step = next(s for s in self.workflow["jobs"][job]["steps"] if s.get("name") == name)
        command = shlex.split(step["run"].replace("\\\n", "").split("\n", 1)[1])
        self.assertEqual(command[1], ".github/skills/test-generation/scripts/validate_ux_gate.py")
        command[0:2] = [sys.executable, str(SCRIPT)]
        command = [
            part.replace("$BASE_SHA", self.base).replace("$HEAD_SHA", head)
            for part in command
        ]
        return subprocess.run(
            command, cwd=self.repo, capture_output=True, text=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )

    def test_design_workflow_accepts_cli_api_but_blocks_missing_visual_brief(self):
        for reason in ("CLI-only", "API-only framework"):
            self.proposal(reason=reason)
            result = self.run_step("stage-design-gate", "Validate proposal and applicable UX brief")
            self.assertEqual(result.returncode, 0, result.stderr)
        self.proposal(True)
        result = self.run_step("stage-design-gate", "Validate proposal and applicable UX brief")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ux-brief.md", result.stderr)
        self.brief()
        self.assertEqual(
            self.run_step("stage-design-gate", "Validate proposal and applicable UX brief").returncode,
            0,
        )

    def test_test_entry_checks_each_active_change_not_archived_examples(self):
        self.proposal()
        visual = self.root / "visual"
        visual.mkdir()
        (visual / "proposal.md").write_text(
            '## UX Applicability\n```json\n{"required":true,"reason":"UI"}\n```\n',
            encoding="utf-8",
        )
        archived = self.root / "archive" / "old"
        archived.mkdir(parents=True)
        (archived / "proposal.md").write_text("# Old proposal\n", encoding="utf-8")
        result = self.run_step("stage-test-gate", "Validate test UX inputs")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("visual", result.stderr)
        (visual / "ux-brief.md").write_text("### UX-01: Keyboard action\n", encoding="utf-8")
        self.assertEqual(self.run_step("stage-test-gate", "Validate test UX inputs").returncode, 0)

    def test_completion_and_security_steps_exempt_nonvisual_but_require_visual_evidence(self):
        for job, name in (
            ("stage-test-gate", "Validate applicable UX completion"),
            ("stage-security-gate", "Require applicable UX validation before security"),
        ):
            self.proposal()
            result = self.run_step(job, name)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.proposal(True)
            self.brief()
            result = self.run_step(job, name)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("ux-validation.json", result.stderr)
            step = next(s for s in self.workflow["jobs"][job]["steps"] if s.get("name") == name)
            self.assertEqual(step["env"]["UX_CHECK_NAMES"], "${{ vars.UX_CHECK_NAMES }}")
            self.assertEqual(self.workflow["jobs"][job]["permissions"]["checks"], "read")

    def test_workflow_rechecks_current_head_and_retains_functional_tests(self):
        for name in ("stage-ux-gate", "stage-design-gate", "stage-test-gate",
                     "stage-security-gate"):
            job = self.workflow["jobs"][name]
            self.assertIn("github.event.pull_request.labels.*.name", job["if"])
            checkout = next(s for s in job["steps"] if s.get("uses", "").startswith("actions/checkout@"))
            self.assertEqual(checkout["with"]["ref"], "${{ github.event.pull_request.head.sha }}")
            self.assertEqual(checkout["with"]["fetch-depth"], 0)
        steps = self.workflow["jobs"]["stage-test-gate"]["steps"]
        self.assertIn("--cov-fail-under=80", next(s["run"] for s in steps if s.get("name") == "Run tests (Python)"))
        self.assertIn("dotnet test", next(s["run"] for s in steps if s.get("name") == "Run tests (.NET)"))


if __name__ == "__main__":
    unittest.main()
