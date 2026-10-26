import json
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "fabric_trace.py"


class TraceIdentityTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp_dir.name) / "repo"
        self.repo.mkdir()
        self.git("init", "-q")
        self.git("config", "user.email", "trace-tests@example.invalid")
        self.git("config", "user.name", "Trace Tests")
        (self.repo / "README.md").write_text("trace test\n", encoding="utf-8")
        self.git("add", "README.md")
        self.git("commit", "-qm", "initial")
        self.change = self.repo / "openspec" / "changes" / "first"
        self.change.mkdir(parents=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def git(self, *args):
        return subprocess.run(
            ["git", "-C", str(self.repo), *args],
            check=True,
            capture_output=True,
            text=True,
        )

    def invoke(self, *args, expected=0):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), *map(str, args)],
            cwd=self.repo,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, expected, result.stderr)
        return result

    def init_trace(self, change_dir=None):
        result = self.invoke(
            "init",
            "--repo",
            self.repo,
            "--change-dir",
            self.change if change_dir is None else change_dir,
        )
        return Path(result.stdout.strip())

    def test_init_binds_identity_to_explicit_change_directory_and_commit(self):
        trace_dir = self.init_trace()
        metadata = json.loads((trace_dir / "trace.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["schemaVersion"], 1)
        self.assertEqual(uuid.UUID(metadata["traceId"]).version, 4)
        self.assertEqual(metadata["repository"]["root"], str(self.repo.resolve()))
        self.assertEqual(metadata["changeDir"], "openspec/changes/first")
        self.assertEqual(metadata["targetRevision"], self.git("rev-parse", "HEAD").stdout.strip())
        self.assertTrue((trace_dir / "policy.json").is_file())
        self.assertTrue((trace_dir / "events.jsonl").is_file())

    def test_duplicate_slug_requires_explicit_directory(self):
        duplicate = self.repo / "spec" / "openspec" / "changes" / "first"
        duplicate.mkdir(parents=True)
        self.invoke("init", "--repo", self.repo, "--change-dir", "first", expected=2)

    def test_explicit_change_directory_in_second_planning_tree(self):
        change = self.repo / "spec" / "openspec" / "changes" / "second"
        change.mkdir(parents=True)
        trace_dir = self.init_trace(change)
        metadata = json.loads((trace_dir / "trace.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["changeDir"], "spec/openspec/changes/second")

    def test_single_slug_is_not_accepted_even_when_unambiguous(self):
        self.invoke("init", "--repo", self.repo, "--change-dir", "first", expected=2)

    def test_unsupported_trace_and_policy_versions_are_rejected(self):
        from scripts import fabric_trace

        with self.assertRaises(fabric_trace.TraceError):
            fabric_trace.validate_trace({"schemaVersion": 999})
        with self.assertRaises(fabric_trace.TraceError):
            fabric_trace.validate_event({"schemaVersion": 999}, {"traceId": "unused"})
        with self.assertRaises(fabric_trace.TraceError):
            fabric_trace.validate_policy({"schemaVersion": 999})

    def test_mismatched_revision_and_repository_are_rejected(self):
        from scripts import fabric_trace

        trace_dir = self.init_trace()
        trace, _ = fabric_trace.load_trace(trace_dir)
        event = {
            "schemaVersion": 1,
            "eventId": str(uuid.uuid4()),
            "traceId": trace["traceId"],
            "timestamp": fabric_trace.utc_now(),
            "kind": "test",
            "stage": "test",
            "provenance": "self-reported",
            "summary": "test",
            "targetRevision": "0" * 40,
        }
        with self.assertRaisesRegex(fabric_trace.TraceError, "revision"):
            fabric_trace.validate_event(event, trace)

        other_repo = Path(self.temp_dir.name) / "other-repo"
        other_repo.mkdir()
        copied = other_repo / ".fabric-traces" / trace["traceId"]
        copied.mkdir(parents=True)
        (copied / "trace.json").write_text(json.dumps(trace), encoding="utf-8")
        (copied / "events.jsonl").write_text("", encoding="utf-8")
        with self.assertRaisesRegex(fabric_trace.TraceError, "contained"):
            fabric_trace.load_trace(copied)

    def test_missing_change_directory_is_rejected(self):
        self.invoke(
            "init",
            "--repo",
            self.repo,
            "--change-dir",
            self.repo / "missing",
            expected=2,
        )


if __name__ == "__main__":
    unittest.main()
