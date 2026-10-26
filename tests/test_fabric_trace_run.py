import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import fabric_trace

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "fabric_trace.py"


class TraceRunTests(unittest.TestCase):
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
        change = self.repo / "openspec" / "changes" / "first"
        change.mkdir(parents=True)
        self.trace_dir = Path(self.invoke(
            "init", "--repo", self.repo, "--change-dir", change
        ).stdout.strip())

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

    def run_command(self, *command, expected=0):
        return self.invoke(
            "run",
            "--trace-dir", self.trace_dir,
            "--stage", "test",
            "--",
            *command,
            expected=expected,
        )

    def events(self):
        trace, paths = fabric_trace.load_trace(self.trace_dir)
        return fabric_trace.read_events(trace, paths["events"])

    def test_success_records_paired_utc_events_and_propagates_output(self):
        result = self.run_command(sys.executable, "-c", "print('child-output')")
        self.assertIn("child-output", result.stdout)
        events = self.events()
        self.assertEqual([event["kind"] for event in events], ["command_started", "command_completed"])
        self.assertEqual(events[0]["invocationId"], events[1]["invocationId"])
        self.assertEqual(events[0]["status"], "running")
        self.assertEqual(events[1]["status"], "succeeded")
        self.assertEqual(events[1]["metadata"]["exitCode"], 0)
        self.assertTrue(all(event["timestamp"].endswith("Z") for event in events))

    def test_documented_run_example_does_not_satisfy_validation_gate(self):
        result = self.invoke(
            "run",
            "--trace-dir", self.trace_dir,
            "--stage", "test",
            "--summary", "Run a harmless local command",
            "--",
            sys.executable,
            "-c",
            "print('example output stays with caller')",
        )

        self.assertIn("example output stays with caller", result.stdout)
        events = self.events()
        self.assertEqual(events[-1]["status"], "succeeded")
        self.assertEqual(events[-1]["metadata"]["exitCode"], 0)
        test_stage = next(
            stage for stage in fabric_trace.evaluate(self.trace_dir)["stages"]
            if stage["stage"] == "test"
        )
        self.assertEqual(test_stage["gateStatus"], "missing")

    def test_child_output_is_visible_but_never_persisted(self):
        output = "trace-output-sentinel"
        argument = "trace-argument-sentinel"
        result = self.run_command(
            sys.executable,
            "-c",
            f"import sys; print('{output}'); print(sys.argv[1])",
            argument,
        )
        self.assertIn(output, result.stdout)
        self.assertIn(argument, result.stdout)
        self.invoke("report", "--trace-dir", self.trace_dir)
        persisted = "\n".join(
            path.read_text(encoding="utf-8")
            for path in self.trace_dir.rglob("*")
            if path.is_file()
        )
        self.assertNotIn(output, persisted)
        self.assertNotIn(argument, persisted)

    def test_nonzero_exit_is_recorded_and_returned(self):
        result = self.run_command(sys.executable, "-c", "raise SystemExit(7)", expected=7)
        events = self.events()
        self.assertEqual(result.returncode, 7)
        self.assertEqual(events[-1]["status"], "failed")
        self.assertEqual(events[-1]["metadata"]["exitCode"], 7)

    def test_process_launch_failure_is_recorded_and_returns_127(self):
        result = self.run_command(
            str(self.repo / "missing-executable"),
            expected=127,
        )
        events = self.events()
        self.assertIn("could not launch command", result.stderr)
        self.assertEqual(events[-1]["status"], "launch-failed")
        self.assertEqual(events[-1]["metadata"]["exitCode"], 127)

    def test_interruption_is_recorded_and_diagnosed(self):
        args = fabric_trace.build_parser().parse_args([
            "run", "--trace-dir", str(self.trace_dir), "--stage", "test",
            "--", sys.executable, "-c", "pass",
        ])
        original_run = subprocess.run

        def interrupt_command(command, **kwargs):
            if command == args.command[1:]:
                raise KeyboardInterrupt
            return original_run(command, **kwargs)

        with patch.object(fabric_trace.subprocess, "run", side_effect=interrupt_command):
            with patch("sys.stderr") as stderr:
                self.assertEqual(fabric_trace.command_run(args), 130)
                self.assertEqual(
                    "".join(call.args[0] for call in stderr.write.call_args_list),
                    "command interrupted\n",
                )

        events = self.events()
        self.assertEqual(events[-1]["status"], "interrupted")
        self.assertEqual(events[-1]["metadata"]["exitCode"], 130)

    def test_missing_completion_remains_running_not_successful(self):
        args = fabric_trace.build_parser().parse_args([
            "run", "--trace-dir", str(self.trace_dir), "--stage", "test",
            "--", sys.executable, "-c", "pass",
        ])
        append_event = fabric_trace.append_event

        def fail_completion(*args, **kwargs):
            if kwargs.get("kind") == "command_completed":
                raise fabric_trace.TraceError("simulated completion write failure")
            return append_event(*args, **kwargs)

        with patch.object(fabric_trace, "append_event", side_effect=fail_completion):
            with self.assertRaisesRegex(fabric_trace.TraceError, "completion write failure"):
                fabric_trace.command_run(args)

        result = fabric_trace.evaluate(self.trace_dir)
        self.assertEqual(result["stages"][3]["gateStatus"], "running")
        self.assertEqual([event["kind"] for event in result["timeline"]], ["command_started"])

    def test_dirty_workspace_is_visible_and_does_not_change_revision(self):
        child = "from pathlib import Path; Path('child-output.txt').write_text('done')"
        self.run_command(sys.executable, "-c", child)
        event = self.events()[-1]
        self.assertTrue(event["metadata"]["workspaceDirtyAtCompletion"])
        self.assertEqual(
            event["metadata"]["startedRevision"],
            event["metadata"]["completedRevision"],
        )
        self.assertTrue(event["metadata"]["targetMatches"])
        result = fabric_trace.evaluate(self.trace_dir)
        test_stage = next(stage for stage in result["stages"] if stage["stage"] == "test")
        self.assertEqual(test_stage["gateStatus"], "missing")

    def test_revision_change_during_command_is_visible(self):
        child = (
            "from pathlib import Path; import subprocess; "
            "Path('revision-change.txt').write_text('changed'); "
            "subprocess.run(['git', 'add', 'revision-change.txt'], check=True); "
            "subprocess.run(['git', 'commit', '-m', 'child revision'], check=True)"
        )
        self.run_command(sys.executable, "-c", child)
        event = self.events()[-1]
        self.assertNotEqual(
            event["metadata"]["startedRevision"],
            event["metadata"]["completedRevision"],
        )
        self.assertFalse(event["metadata"]["targetMatches"])


if __name__ == "__main__":
    unittest.main()
