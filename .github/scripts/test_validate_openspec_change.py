"""Fixture coverage for the bounded archive artifact validator."""

from contextlib import redirect_stderr, redirect_stdout
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from validate_openspec_change import OpenSpecValidationError, main, validate_change


class ValidateOpenSpecChangeTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / "policy-change"
        self.root.mkdir()
        for name in ("proposal.md", "design.md"):
            (self.root / name).write_text("# Complete planning\n", encoding="utf-8")
        self.tasks = self.root / "tasks.md"
        self.tasks.write_text("- [x] 1.1 Complete behavior and verification\n", encoding="utf-8")
        self.spec = self.root / "specs" / "domain" / "spec.md"
        self.spec.parent.mkdir(parents=True)
        self.spec.write_text(
            "## ADDED Requirements\n\n### Requirement: Complete planning\n"
            "The workflow MUST require planning.\n\n#### Scenario: Missing planning\n"
            "- WHEN planning is missing\n- THEN implementation stops\n",
            encoding="utf-8",
        )

    def test_complete_tasks_pass_without_certifying_external_gates(self) -> None:
        self.tasks.write_text(
            "# Tasks\n- [ x] Complete\n  * [X ] Also complete\n"
            "+ [x] Third task\n1. [x] Fourth task\n"
            "## Workflow follow-up\n- Archive after review\n",
            encoding="utf-8",
        )
        validate_change(self.root)
        output = io.StringIO()
        with patch("sys.argv", ["validate", self.root.name, "--root", str(self.root.parent)]):
            with redirect_stdout(output):
                self.assertEqual(main(), 0)
        self.assertIn("External quality gates, acceptance, and spec sync", output.getvalue())
        self.assertNotIn("archive readiness passed", output.getvalue())

    def test_missing_and_empty_required_artifacts_fail(self) -> None:
        for name in ("proposal.md", "design.md", "tasks.md"):
            path = self.root / name
            original = path.read_text(encoding="utf-8")
            with self.subTest(name=name, state="missing"):
                path.unlink()
                with self.assertRaisesRegex(OpenSpecValidationError, "missing required"):
                    validate_change(self.root)
            with self.subTest(name=name, state="empty"):
                path.write_text(" \n\t", encoding="utf-8")
                with self.assertRaisesRegex(OpenSpecValidationError, "empty required"):
                    validate_change(self.root)
            path.write_text(original, encoding="utf-8")

    def test_incomplete_or_unknown_markers_cannot_hide_behind_completed_tasks(self) -> None:
        for marker in (" ", "", "~", "-", "?", "xx", "done"):
            for prefix in ("-", "  *", "+", "1."):
                with self.subTest(marker=marker, prefix=prefix):
                    self.tasks.write_text(
                        f"- [x] Complete\n{prefix} [{marker}] Still unfinished\n",
                        encoding="utf-8",
                    )
                    with self.assertRaisesRegex(OpenSpecValidationError, "1 incomplete"):
                        validate_change(self.root)

    def test_no_usable_tasks_or_undescribed_tasks_fail(self) -> None:
        for tasks in (
            "# Tasks\n- Plain prose only\n",
            "# Tasks\n- [x]\n",
            "- [x] Complete\n- [x]\n",
            "```markdown\n- [x] Example only\n```\n",
            "~~~md\n- [x] Example only\n~~~\n",
        ):
            with self.subTest(tasks=tasks):
                self.tasks.write_text(tasks, encoding="utf-8")
                with self.assertRaises(OpenSpecValidationError):
                    validate_change(self.root)

    def test_fenced_examples_do_not_count_as_unfinished_tasks(self) -> None:
        self.tasks.write_text(
            "- [x] Actual task\n````md\n- [ ] Example\n```\n"
            "- [ ] Still in outer fence\n````\n",
            encoding="utf-8",
        )
        validate_change(self.root)

    def test_language_tagged_fence_line_does_not_hide_unfinished_tasks(self) -> None:
        self.tasks.write_text(
            "- [x] Actual task\n```md\n- [ ] Example\n```markdown\n"
            "- [ ] Still in outer fence\n```\n- [ ] Unfinished task\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(OpenSpecValidationError, "1 incomplete"):
            validate_change(self.root)

    def test_outdented_task_after_nested_unclosed_fence_still_fails(self) -> None:
        self.tasks.write_text(
            "- [x] Parent task\n  ```md\n  - [ ] Example only\n- [ ] Actual unfinished task\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(OpenSpecValidationError, "1 incomplete"):
            validate_change(self.root)

    def test_nested_specs_are_checked_and_empty_specs_fail(self) -> None:
        nested = self.spec.parent / "nested" / "spec.md"
        nested.parent.mkdir()
        self.spec.rename(nested)
        validate_change(self.root)
        for text, error in (
            (" ", "empty delta"),
            ("# No delta\n", "no requirement section"),
            ("## ADDED Requirements\n", "no requirement:"),
        ):
            with self.subTest(text=text):
                nested.write_text(text, encoding="utf-8")
                with self.assertRaisesRegex(OpenSpecValidationError, error):
                    validate_change(self.root)

    def test_missing_specs_fail(self) -> None:
        self.spec.unlink()
        with self.assertRaisesRegex(OpenSpecValidationError, "no delta specs"):
            validate_change(self.root)

    def test_domainless_root_spec_does_not_count_as_a_delta(self) -> None:
        self.spec.unlink()
        root_spec = self.root / "specs" / "spec.md"
        root_spec.write_text(
            "## ADDED Requirements\n\n### Requirement: Domainless\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(OpenSpecValidationError, "no delta specs"):
            validate_change(self.root)

    def test_rename_only_delta_keeps_the_canonical_from_to_format(self) -> None:
        self.spec.write_text(
            "## RENAMED Requirements\n"
            "- FROM: `### Requirement: Old name`\n"
            "- TO: `### Requirement: New name`\n",
            encoding="utf-8",
        )
        validate_change(self.root)

    def test_read_errors_are_explicit_cli_failures(self) -> None:
        error = io.StringIO()
        with patch("sys.argv", ["validate", self.root.name, "--root", str(self.root.parent)]):
            with patch.object(Path, "read_text", side_effect=PermissionError("read denied")):
                with redirect_stderr(error):
                    self.assertEqual(main(), 1)
        self.assertIn("artifact read failed: read denied", error.getvalue())


if __name__ == "__main__":
    unittest.main()
