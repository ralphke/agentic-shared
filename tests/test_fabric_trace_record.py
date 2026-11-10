import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import fabric_trace

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "fabric_trace.py"


class TraceRecordTests(unittest.TestCase):
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

    def record(self, kind, stage, *args, expected=0):
        return self.invoke(
            "record",
            "--trace-dir", self.trace_dir,
            "--kind", kind,
            "--stage", stage,
            "--summary", "reported success",
            *args,
            expected=expected,
        )

    def test_manual_activity_kinds_are_distinct_and_self_reported(self):
        expected_kinds = (
            ("instruction_discovery", "proposal"),
            ("instruction_inclusion", "design"),
            ("skill_load", "implement"),
            ("agent_invocation", "test"),
            ("stage_claim", "security"),
        )
        for kind, stage in expected_kinds:
            self.record(kind, stage)

        trace, paths = fabric_trace.load_trace(self.trace_dir)
        events = fabric_trace.read_events(trace, paths["events"])
        self.assertEqual([event["kind"] for event in events], [kind for kind, _ in expected_kinds])
        self.assertTrue(all(event["provenance"] == "self-reported" for event in events))
        self.assertTrue(all("status" not in event for event in events))

    def test_documented_record_example_is_self_reported(self):
        self.invoke(
            "record",
            "--trace-dir", self.trace_dir,
            "--kind", "skill_load",
            "--stage", "implement",
            "--summary", "Loaded the local fabric-trace skill",
        )

        trace, paths = fabric_trace.load_trace(self.trace_dir)
        events = fabric_trace.read_events(trace, paths["events"])
        self.assertEqual(events[0]["kind"], "skill_load")
        self.assertEqual(events[0]["summary"], "Loaded the local fabric-trace skill")
        self.assertEqual(events[0]["provenance"], "self-reported")
        self.assertNotIn("status", events[0])

    def test_manual_records_cannot_select_provenance_or_status(self):
        base = ["--trace-dir", self.trace_dir, "--kind", "stage_claim", "--stage", "test", "--summary", "claim"]
        for option, value in (("--provenance", "provider-verified"), ("--status", "verified")):
            result = self.invoke("record", *base, option, value, expected=2)
            self.assertIn(option, result.stderr)

        result = self.record(
            "stage_claim",
            "test",
            "--metadata-json",
            json.dumps({"status": "verified"}),
            expected=2,
        )
        self.assertIn("unsupported metadata fields: status", result.stderr)

    def test_fabricated_success_and_session_reference_do_not_satisfy_gates(self):
        for stage in fabric_trace.STAGES:
            args = ["--session-ref", "session://unverified/example"]
            self.record("stage_claim", stage, *args)

        trace, paths = fabric_trace.load_trace(self.trace_dir)
        events = fabric_trace.read_events(trace, paths["events"])
        self.assertTrue(all(event["provenance"] == "self-reported" for event in events))
        self.assertTrue(all(event.get("status") is None for event in events))
        for event in events:
            self.assertEqual(event["references"], [{
                "type": "self-reported-session",
                "value": "session://unverified/example",
            }])

        result = fabric_trace.evaluate(self.trace_dir)
        self.assertEqual(result["status"], "incomplete")
        self.assertTrue(all(stage["gateStatus"] == "missing" for stage in result["stages"]))
        self.invoke("check", "--trace-dir", self.trace_dir, expected=1)

    def test_metadata_allowlist_rejects_raw_fields_and_secret_values(self):
        for metadata in (
            {"result": {"arguments": ["argument-sentinel"]}},
            {"result": {"detail": "token=metadata-sentinel"}},
        ):
            result = self.record(
                "stage_claim",
                "test",
                "--metadata-json",
                json.dumps(metadata),
                expected=2,
            )
            self.assertIn("metadata", result.stderr)
        events = (self.trace_dir / "events.jsonl").read_text(encoding="utf-8")
        self.assertNotIn("argument-sentinel", events)
        self.assertNotIn("metadata-sentinel", events)

    def test_persisted_metadata_redacts_values_and_rejects_unsafe_keys(self):
        trace, paths = fabric_trace.load_trace(self.trace_dir)
        event = fabric_trace.append_event(
            trace,
            paths,
            kind="provider_observation",
            stage="test",
            summary="provider token=summary-sentinel",
            provenance="collector-observed",
            metadata={"result": {"detail": "pass" + "word" + "=metadata-sentinel"}},
        )
        serialized = paths["events"].read_text(encoding="utf-8")
        self.assertNotIn("summary-sentinel", serialized)
        self.assertNotIn("metadata-sentinel", serialized)
        self.assertIn("[REDACTED]", serialized)
        self.assertEqual(
            event["metadata"]["result"]["detail"],
            "[REDACTED]",
        )

        with self.assertRaisesRegex(fabric_trace.TraceError, "sensitive field"):
            fabric_trace.append_event(
                trace,
                paths,
                kind="provider_observation",
                stage="test",
                summary="provider observation",
                provenance="collector-observed",
                metadata={"result": {"stdout": "output-sentinel"}},
            )
        self.assertNotIn("output-sentinel", paths["events"].read_text(encoding="utf-8"))

    def test_url_sanitization_and_markdown_escaping(self):
        result = self.record(
            "stage_claim",
            "test",
            "--summary",
            "review | <untrusted> `text`",
            "--url",
            "https://example.invalid/review?access%5Ftoken=url-sentinel&view=1",
        )
        trace, paths = fabric_trace.load_trace(self.trace_dir)
        event = fabric_trace.read_events(trace, paths["events"])[0]
        self.assertIn("access_token=[REDACTED]", event["references"][0]["value"])
        self.assertNotIn("url-sentinel", paths["events"].read_text(encoding="utf-8"))
        self.invoke("report", "--trace-dir", self.trace_dir)
        report_json = paths["report_json"].read_text(encoding="utf-8")
        report_md = paths["report_md"].read_text(encoding="utf-8")
        self.assertNotIn("url-sentinel", report_json + report_md)
        self.assertIn(r"\|", report_md)
        self.assertIn("&lt;untrusted&gt;", report_md)
        self.assertIn(r"\`text\`", report_md)
        self.assertIn(event["eventId"], report_md)
        self.assertIn("self-reported", report_md)
        self.assertIn(
            fabric_trace.escape_markdown(event["references"][0]["value"]),
            report_md,
        )

    def test_reports_share_partial_evaluation_and_include_required_details(self):
        self.record(
            "stage_claim",
            "test",
            "--url",
            "https://example.invalid/evidence/123",
        )
        trace, paths = fabric_trace.load_trace(self.trace_dir)
        event = fabric_trace.read_events(trace, paths["events"])[0]

        self.invoke("report", "--trace-dir", self.trace_dir)
        report = json.loads(paths["report_json"].read_text(encoding="utf-8"))
        report_markdown = paths["report_md"].read_text(encoding="utf-8")
        check = self.invoke("check", "--trace-dir", self.trace_dir, expected=1)
        checked = json.loads(check.stdout)

        self.assertEqual(report["status"], "incomplete")
        self.assertEqual(report["stages"], checked["stages"])
        self.assertEqual(report["timeline"], checked["timeline"])
        self.assertEqual(
            tuple(stage["stage"] for stage in report["stages"]),
            fabric_trace.STAGES,
        )
        self.assertIn(report["targetRevision"], report_markdown)
        self.assertIn(report["policyDigest"], report_markdown)
        self.assertIn(report["observationBoundary"], report_markdown)
        self.assertIn(event["eventId"], report_markdown)
        self.assertIn(
            fabric_trace.escape_markdown(event["references"][0]["value"]),
            report_markdown,
        )
        self.assertIn(event["provenance"], report_markdown)
        self.assertIn("## Next evidence", report_markdown)

    def test_report_and_check_return_explicit_invalid_trace_errors(self):
        missing_trace = self.repo / ".fabric-traces" / "missing-trace"
        for command in ("report", "check"):
            with self.subTest(command=command):
                result = self.invoke(
                    command, "--trace-dir", missing_trace, expected=2
                )
                self.assertIn("fabric-trace:", result.stderr)
                self.assertIn("trace", result.stderr.lower())

    def test_unsafe_url_schemes_and_embedded_credentials_are_rejected(self):
        for url in (
            "file:///tmp/private",
            "https://user" + ":password" + "@example.invalid/path",
            "https://example.invalid:invalid/path",
        ):
            with self.subTest(url=url):
                with self.assertRaises(fabric_trace.TraceError):
                    fabric_trace.safe_url(url)


if __name__ == "__main__":
    unittest.main()
