import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "fabric_trace.py"
SKILL = ROOT / ".github" / "skills" / "local" / "fabric-trace" / "SKILL.md"


class FabricTraceSkillTests(unittest.TestCase):
    def test_frontmatter_triggers_and_referenced_files(self):
        content = SKILL.read_text(encoding="utf-8")
        sections = content.split("---", 2)
        self.assertEqual(len(sections), 3)
        frontmatter = sections[1]
        self.assertIn("name: fabric-trace", frontmatter)
        self.assertIn("trace a Software Fabric change", frontmatter)
        self.assertIn("record a Fabric execution trace", frontmatter)
        self.assertIn("run OpenSpec apply with tracing", frontmatter)
        self.assertIn("check a Fabric trace", frontmatter)
        self.assertIn("openspec-apply-change", sections[2])
        self.assertIn("/openspec-apply-change <change>", sections[2])

        references = [
            target
            for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", sections[2])
            if not target.startswith(("https://", "http://"))
        ]
        self.assertTrue(references)
        for reference in references:
            with self.subTest(reference=reference):
                self.assertTrue((SKILL.parent / reference).resolve().is_file())

    def test_documented_local_flow_uses_temporary_repository(self):
        with tempfile.TemporaryDirectory() as temporary_dir:
            repo = Path(temporary_dir) / "repo"
            repo.mkdir()
            self.git(repo, "init", "-q")
            self.git(repo, "config", "user.email", "trace-skill@example.invalid")
            self.git(repo, "config", "user.name", "Trace Skill Test")
            change_dir = repo / "openspec" / "changes" / "sample"
            change_dir.mkdir(parents=True)
            tests_dir = repo / "tests"
            tests_dir.mkdir()
            (tests_dir / "test_smoke.py").write_text(
                "import unittest\n\n"
                "class SmokeTests(unittest.TestCase):\n"
                "    def test_trace_flow(self):\n"
                "        self.assertTrue(True)\n",
                encoding="utf-8",
            )
            self.git(repo, "add", ".")
            self.git(repo, "commit", "-qm", "initial")

            initialized = self.cli(
                repo, "init", "--repo", ".", "--change-dir",
                "openspec/changes/sample",
            )
            trace_dir = Path(initialized.stdout.strip())
            self.cli(
                repo, "record",
                "--trace-dir", trace_dir,
                "--kind", "skill_load",
                "--stage", "implement",
                "--summary", "Loaded the local fabric-trace skill",
            )
            self.cli(
                repo, "run",
                "--trace-dir", trace_dir,
                "--stage", "test",
                "--summary", "Run focused tests",
                "--", sys.executable, "-m", "unittest", "discover",
                "-s", "tests", "-p", "test_smoke.py",
            )
            self.cli(repo, "report", "--trace-dir", trace_dir)
            check = self.cli(repo, "check", "--trace-dir", trace_dir, expected=1)

            report = json.loads((trace_dir / "report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "incomplete")
            self.assertEqual(len(report["stages"]), 9)
            self.assertIn("other host activity is outside the trace", report["observationBoundary"])
            self.assertEqual(json.loads(check.stdout)["status"], report["status"])

    def git(self, repo, *args):
        return subprocess.run(
            ["git", "-C", str(repo), *args],
            check=True,
            capture_output=True,
            text=True,
        )

    def cli(self, cwd, *args, expected=0):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), *map(str, args)],
            cwd=cwd,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, expected, result.stderr)
        return result


if __name__ == "__main__":
    unittest.main()
