"""Fixture tests for bounded post-generation policy restoration."""

from __future__ import annotations

from contextlib import redirect_stderr
import io
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from restore_openspec_contracts import (
    END,
    ROOT,
    START,
    TARGETS,
    RestorationError,
    main,
    restore,
    restored_content,
)


class RestoreOpenSpecContractsTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        for target in TARGETS:
            name = f"name: {target.skill_name}\n" if target.skill_name else ""
            content = (
                f"---\n{name}description: Generated fixture\n"
                "metadata:\n  generatedBy: '1.14.3'\n---\n\n"
                f"{target.intro}\n\n"
                "**Store selection:** Keep the selected --store <id>.\n\n"
                "**Project check:** Keep the resolved root.\n"
            )
            path = self.root / target.path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content.encode("utf-8"))

    def snapshot(self) -> dict[Path, bytes]:
        return {
            target.path: (self.root / target.path).read_bytes()
            for target in TARGETS
            if (self.root / target.path).exists()
        }

    def test_regenerated_fixtures_preserve_all_surrounding_bytes_and_newlines(self) -> None:
        for newline in (b"\n", b"\r\n"):
            with self.subTest(newline=newline):
                before = self.snapshot()
                for target in TARGETS:
                    path = self.root / target.path
                    original = before[target.path]
                    # Strip only the known block between newline variants.
                    for style in (b"\n", b"\r\n"):
                        original = original.replace(target.block(style), b"")
                    path.write_bytes(original.replace(b"\r\n", b"\n").replace(b"\n", newline))
                regenerated = self.snapshot()
                self.assertTrue(all(m.startswith("Restored:") for m in restore(self.root)))
                for target in TARGETS:
                    actual = (self.root / target.path).read_bytes()
                    self.assertEqual(actual.count(target.block(newline)), 1)
                    self.assertEqual(actual.replace(target.block(newline), b""), regenerated[target.path])
                after = self.snapshot()
                mtimes = {t.path: (self.root / t.path).stat().st_mtime_ns for t in TARGETS}
                self.assertTrue(all(m.startswith("Already correct:") for m in restore(self.root)))
                self.assertEqual(self.snapshot(), after)
                self.assertEqual(
                    mtimes, {t.path: (self.root / t.path).stat().st_mtime_ns for t in TARGETS}
                )

    def test_preflight_failures_leave_every_target_unchanged(self) -> None:
        target = TARGETS[-1]
        path = self.root / target.path
        original = path.read_bytes()
        block = target.block(b"\n")
        mutations = {
            "missing file": None,
            "invalid YAML": original.replace(b"description: Generated fixture", b"description: ["),
            "nonmapping YAML": b"---\n- value\n---\n\n" + original.split(b"---\n\n", 1)[1],
            "empty description": original.replace(b"description: Generated fixture", b"description: ''"),
            "duplicate anchor": original + b"\n" + target.intro.encode() + b"\n",
            "missing anchor": original.replace(target.intro.encode(), b"Unknown introduction"),
            "malformed marker": original + START.encode(),
            "orphan end": original + END.encode(),
            "misplaced block": original + block,
            "conflicting block": restored_content(target, original).replace(b"Deprecated:", b"Changed:"),
            "duplicate block": restored_content(target, original) + block,
            "unsupported layout": original.replace(target.intro.encode(), b"Extra\n\n" + target.intro.encode()),
            "invalid encoding": original + b"\xff",
            "missing frontmatter": original[4:],
        }
        for label, mutation in mutations.items():
            with self.subTest(label=label):
                if mutation is None:
                    path.unlink()
                else:
                    path.write_bytes(mutation)
                before = self.snapshot()
                with self.assertRaisesRegex(RestorationError, str(target.path).replace("\\", "\\\\")):
                    restore(self.root)
                self.assertEqual(self.snapshot(), before)
                path.write_bytes(original)

    def test_wrong_skill_name_is_rejected_before_any_writes(self) -> None:
        target = TARGETS[2]
        path = self.root / target.path
        path.write_bytes(path.read_bytes().replace(target.skill_name.encode(), b"other-skill", 1))
        before = self.snapshot()
        with self.assertRaisesRegex(RestorationError, "frontmatter name"):
            restore(self.root)
        self.assertEqual(self.snapshot(), before)

    def test_committed_policy_blocks_match_script_without_rewrites(self) -> None:
        for target in TARGETS:
            with self.subTest(target=target.path):
                original = (ROOT / target.path).read_bytes()
                self.assertEqual(restored_content(target, original), original)
                newline = b"\r\n" if original.startswith(b"---\r\n") else b"\n"
                regenerated = original.replace(target.block(newline), b"")
                self.assertNotEqual(regenerated, original)
                self.assertEqual(restored_content(target, regenerated), original)

    def test_read_error_is_explicit_and_prevents_writes(self) -> None:
        before = self.snapshot()
        real_read = Path.read_bytes

        def read(path: Path) -> bytes:
            if path == self.root / TARGETS[-1].path:
                raise PermissionError("fixture read denied")
            return real_read(path)

        with patch.object(Path, "read_bytes", read):
            with self.assertRaisesRegex(RestorationError, "cannot read target.*read denied"):
                restore(self.root)
        self.assertEqual(self.snapshot(), before)

    def test_write_error_reports_completed_writes(self) -> None:
        real_write = Path.write_bytes

        def write(path: Path, data: bytes) -> int:
            if path == self.root / TARGETS[1].path:
                raise PermissionError("fixture write denied")
            return real_write(path, data)

        with patch.object(Path, "write_bytes", write):
            with self.assertRaises(RestorationError) as raised:
                restore(self.root)
        self.assertIn("fixture write denied", str(raised.exception))
        self.assertIn(f"completed writes: {TARGETS[0].path}", str(raised.exception))

    def test_concurrent_change_is_not_overwritten(self) -> None:
        real_read = Path.read_bytes
        reads = 0

        def read(path: Path) -> bytes:
            nonlocal reads
            data = real_read(path)
            if path == self.root / TARGETS[0].path:
                reads += 1
                if reads == 2:
                    return data + b"\nconcurrent edit\n"
            return data

        before = self.snapshot()
        with patch.object(Path, "read_bytes", read):
            with self.assertRaisesRegex(RestorationError, "changed since preflight"):
                restore(self.root)
        self.assertEqual(self.snapshot(), before)

    def test_cli_failure_is_nonzero_and_actionable(self) -> None:
        (self.root / TARGETS[-1].path).unlink()
        output = io.StringIO()
        with patch("restore_openspec_contracts.ROOT", self.root), redirect_stderr(output):
            self.assertEqual(main(), 1)
        self.assertIn("Restoration failed:", output.getvalue())
        self.assertIn("cannot read target", output.getvalue())

    def test_cli_uses_its_repository_not_working_directory(self) -> None:
        script = self.root / ".github" / "scripts" / "restore_openspec_contracts.py"
        script.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / ".github" / "scripts" / script.name, script)
        command = [sys.executable, str(script)]
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn(
            r".\.venv\Scripts\python.exe .github\scripts\restore_openspec_contracts.py",
            readme,
        )
        first = subprocess.run(
            [sys.executable, str(Path(".github") / "scripts" / script.name)],
            cwd=self.root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout.count("Restored:"), 6)
        before = self.snapshot()
        second = subprocess.run(command, cwd=self.root.parent, capture_output=True, text=True)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(second.stdout.count("Already correct:"), 6)
        self.assertEqual(self.snapshot(), before)

    def test_readme_documents_update_restoration_and_validation(self) -> None:
        content = (ROOT / "README.md").read_text(encoding="utf-8")
        for phrase in (
            "Option 2(b)",
            "openspec --version",
            "Before any `openspec init`, back up",
            "openspec update",
            "restore_openspec_contracts.py",
            r"git diff -- .github\skills .github\prompts",
            "openspec context --json",
            r'.\.venv\Scripts\python.exe -m unittest discover -s .github\scripts -p "test_*.py"',
            "pip install PyYAML",
            '$env:PYTHONDONTWRITEBYTECODE = "1"',
            "must not repair the checkout",
            "branch protection separately",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, content)


if __name__ == "__main__":
    unittest.main()
