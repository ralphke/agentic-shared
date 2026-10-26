import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import fabric_trace

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "fabric_trace.py"


class TraceStorageTests(unittest.TestCase):
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
        self.trace_dir = Path(self.invoke("init", "--repo", self.repo, "--change-dir", self.change).stdout.strip())
        self.trace, self.paths = fabric_trace.load_trace(self.trace_dir)

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

    def test_events_persist_across_cli_processes(self):
        event_ids = []
        for index in range(3):
            event_ids.append(self.invoke(
                "record",
                "--trace-dir", self.trace_dir,
                "--kind", "stage_claim",
                "--stage", "implement",
                "--summary", f"process {index}",
            ).stdout.strip())
        events = fabric_trace.read_events(self.trace, self.paths["events"])
        self.assertEqual([event["eventId"] for event in events], event_ids)
        self.assertEqual([event["summary"] for event in events], ["process 0", "process 1", "process 2"])

    def test_concurrent_cli_writers_append_complete_events(self):
        processes = [
            subprocess.Popen(
                [
                    sys.executable, str(SCRIPT), "record",
                    "--trace-dir", str(self.trace_dir),
                    "--kind", "stage_claim",
                    "--stage", "implement",
                    "--summary", f"writer {index}",
                ],
                cwd=self.repo,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            for index in range(12)
        ]
        for process in processes:
            stdout, stderr = process.communicate(timeout=15)
            self.assertEqual(process.returncode, 0, stderr)
            self.assertTrue(stdout.strip())
        events = fabric_trace.read_events(self.trace, self.paths["events"])
        self.assertEqual(len(events), 12)
        self.assertEqual(len({event["eventId"] for event in events}), 12)

    def test_malformed_and_truncated_streams_are_reported(self):
        path = self.paths["events"]
        valid_event = fabric_trace.append_event(
            self.trace,
            self.paths,
            kind="test",
            stage="test",
            summary="valid event",
            provenance="self-reported",
        )
        path.write_bytes(b"{not-json")
        with self.assertRaisesRegex(fabric_trace.TraceError, r"line 1 .*possibly truncated"):
            fabric_trace.read_events(self.trace, path)

        path.write_bytes(fabric_trace.canonical_json(valid_event) + b"\n{not-json\n")
        with self.assertRaisesRegex(fabric_trace.TraceError, r"line 2 .*possibly truncated"):
            fabric_trace.read_events(self.trace, path)

    def test_append_refuses_to_extend_a_malformed_stream(self):
        self.paths["events"].write_bytes(b"{not-json")
        with self.assertRaisesRegex(fabric_trace.TraceError, "possibly truncated"):
            fabric_trace.append_event(
                self.trace,
                self.paths,
                kind="test",
                stage="test",
                summary="test event",
                provenance="self-reported",
            )

    def test_lock_conflicts_and_stale_locks_are_explicit(self):
        lock_path = self.paths["events"].with_suffix(".jsonl.lock")
        with fabric_trace.FileLock(lock_path):
            with self.assertRaisesRegex(fabric_trace.TraceError, "conflicting writer"):
                with fabric_trace.FileLock(lock_path, timeout=0.02):
                    self.fail("conflicting writer unexpectedly acquired the lock")

        lock_path.write_text("stale", encoding="utf-8")
        old = time.time() - 301
        os.utime(lock_path, (old, old))
        with self.assertRaisesRegex(fabric_trace.TraceError, "stale lock"):
            with fabric_trace.FileLock(lock_path, stale_after=300):
                self.fail("stale lock unexpectedly acquired")

    def test_atomic_write_preserves_existing_file_when_replace_fails(self):
        target = self.trace_dir / "report.json"
        target.write_bytes(b"previous")
        with patch.object(fabric_trace.os, "replace", side_effect=OSError("replace failed")):
            with self.assertRaisesRegex(OSError, "replace failed"):
                fabric_trace.atomic_write(target, b"new")
        self.assertEqual(target.read_bytes(), b"previous")
        self.assertEqual(list(self.trace_dir.glob(".report.json.*")), [])

    def test_init_rejects_noncanonical_and_escaping_output_paths(self):
        for output_dir in ("other-traces", "../outside"):
            result = subprocess.run(
                [
                    sys.executable, str(SCRIPT), "init",
                    "--repo", str(self.repo),
                    "--change-dir", str(self.change),
                    "--output-dir", output_dir,
                ],
                cwd=self.repo,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn("trace output directory", result.stderr)

    def test_trace_subdirectory_must_match_identity_and_cannot_escape(self):
        misplaced = self.repo / ".fabric-traces" / "nested" / self.trace["traceId"]
        misplaced.mkdir(parents=True)
        (misplaced / "trace.json").write_text(json.dumps(self.trace), encoding="utf-8")
        (misplaced / "events.jsonl").write_text("", encoding="utf-8")
        with self.assertRaisesRegex(fabric_trace.TraceError, r"<traceId>"):
            fabric_trace.load_trace(misplaced)

        external_events = self.repo.parent / "outside-events.jsonl"
        with self.assertRaisesRegex(fabric_trace.TraceError, "events path"):
            fabric_trace.ensure_contained(self.trace_dir, external_events, "trace events path")


if __name__ == "__main__":
    unittest.main()
