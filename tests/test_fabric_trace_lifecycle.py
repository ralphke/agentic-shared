import argparse
import copy
import hashlib
import io
import json
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from scripts import fabric_trace


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "fabric_trace"
POSITIVE_FIXTURE = FIXTURE_DIR / "full_lifecycle.json"
NEGATIVE_FIXTURE = FIXTURE_DIR / "negative_evidence.json"


class FabricTraceLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.full_fixture = json.loads(POSITIVE_FIXTURE.read_text(encoding="utf-8"))
        self.negative_fixture = json.loads(NEGATIVE_FIXTURE.read_text(encoding="utf-8"))

    def test_simulated_full_lifecycle_is_complete_and_marked_in_both_reports(self):
        with tempfile.TemporaryDirectory() as temporary_dir:
            repo, change_dir, policy_path = self.create_repository(Path(temporary_dir))
            trace_dir = self.create_trace(
                repo, change_dir, policy_path,
                simulation=self.full_fixture["simulation"],
            )
            self.append_fixture_events(trace_dir)

            result = fabric_trace.evaluate(trace_dir)
            self.assertEqual(result["status"], "verified-complete")
            self.assertEqual(len(result["stages"]), len(fabric_trace.STAGES))
            self.assertTrue(result["simulation"])
            report_status, _, report_error = self.invoke_main(
                "report", "--trace-dir", trace_dir,
            )
            check_status, check_output, check_error = self.invoke_main(
                "check", "--trace-dir", trace_dir,
            )

            report = json.loads((trace_dir / "report.json").read_text(encoding="utf-8"))
            markdown = (trace_dir / "report.md").read_text(encoding="utf-8")
            self.assertEqual(report_status, 0, report_error)
            self.assertEqual(check_status, 0, check_error)
            checked = json.loads(check_output)
            self.assertEqual(checked["status"], "verified-complete")
            self.assertEqual(report["status"], "verified-complete")
            self.assertIs(report["simulation"], True)
            self.assertEqual(
                [stage["stage"] for stage in report["stages"]],
                list(fabric_trace.STAGES),
            )
            self.assertEqual(
                [stage["stage"] for stage in checked["stages"]],
                list(fabric_trace.STAGES),
            )
            self.assertIn("YES — fixture-backed simulation, not a real deployment", markdown)
            self.assertIn("- Status: **verified-complete**", markdown)
            for stage in fabric_trace.STAGES:
                self.assertIn(f"| {stage} |", markdown)

    def test_missing_deploy_and_operate_evidence_prevents_completion(self):
        with tempfile.TemporaryDirectory() as temporary_dir:
            repo, change_dir, policy_path = self.create_repository(Path(temporary_dir))
            trace_dir = self.create_trace(repo, change_dir, policy_path, simulation=True)
            missing = set(self.negative_fixture["missingStages"])
            self.append_fixture_events(
                trace_dir,
                included_stages=set(fabric_trace.STAGES) - missing,
            )

            result = fabric_trace.evaluate(trace_dir)
            gates = {stage["stage"]: stage["gateStatus"] for stage in result["stages"]}
            self.assertEqual(result["status"], "incomplete")
            self.assertEqual(gates["deploy"], "missing")
            self.assertEqual(gates["operate"], "missing")
            check_status, _, _ = self.invoke_main("check", "--trace-dir", trace_dir)
            self.assertEqual(check_status, 1)

    def test_missing_legal_assessment_remains_missing(self):
        with tempfile.TemporaryDirectory() as temporary_dir:
            repo, change_dir, policy_path = self.create_repository(Path(temporary_dir))
            trace_dir = self.create_trace(repo, change_dir, policy_path, simulation=True)

            result = fabric_trace.evaluate(trace_dir)
            legal = next(stage for stage in result["stages"] if stage["stage"] == "legal")
            self.assertEqual(legal["gateStatus"], "missing")
            self.assertEqual(result["status"], "incomplete")

    def test_high_risk_legal_evidence_without_clearance_blocks_completion(self):
        with tempfile.TemporaryDirectory() as temporary_dir:
            repo, change_dir, policy_path = self.create_repository(Path(temporary_dir))
            trace_dir = self.create_trace(repo, change_dir, policy_path, simulation=True)
            trace, paths = fabric_trace.load_trace(trace_dir)
            evidence = self.replace_tokens(
                self.negative_fixture["highRiskLegalWithoutClearance"],
                {"$REVISION": trace["targetRevision"]},
            )
            fabric_trace.append_event(
                trace,
                paths,
                kind="fixture_evidence_observed",
                stage="legal",
                summary="Fixture high-risk legal assessment",
                provenance="collector-observed",
                status="verified",
                metadata={
                    "producer": self.local_producer("legal"),
                    "evidence": evidence,
                },
            )

            result = fabric_trace.evaluate(trace_dir)
            legal = next(stage for stage in result["stages"] if stage["stage"] == "legal")
            self.assertEqual(legal["gateStatus"], "failed")
            self.assertIn("requires explicit clearance", legal["reasons"][0])
            self.assertEqual(result["status"], "incomplete")

    def test_forged_all_stage_activity_does_not_satisfy_evidence_contracts(self):
        with tempfile.TemporaryDirectory() as temporary_dir:
            repo, change_dir, policy_path = self.create_repository(Path(temporary_dir))
            trace_dir = self.create_trace(repo, change_dir, policy_path, simulation=True)
            trace, paths = fabric_trace.load_trace(trace_dir)
            for stage in fabric_trace.STAGES:
                fabric_trace.append_event(
                    trace,
                    paths,
                    kind=self.negative_fixture["forgedActivity"]["kind"],
                    stage=stage,
                    summary=self.negative_fixture["forgedActivity"]["summary"],
                    provenance="self-reported",
                )

            result = fabric_trace.evaluate(trace_dir)
            self.assertEqual(result["status"], "incomplete")
            self.assertTrue(all(stage["activityStatus"] == "observed" for stage in result["stages"]))
            self.assertTrue(all(stage["gateStatus"] != "verified" for stage in result["stages"]))

    def test_changed_policy_is_rejected_and_new_revision_does_not_inherit_gates(self):
        with tempfile.TemporaryDirectory() as temporary_dir:
            root = Path(temporary_dir)
            repo, change_dir, policy_path = self.create_repository(root)
            previous_trace = self.create_trace(
                repo, change_dir, policy_path, simulation=True,
            )
            self.append_fixture_events(previous_trace)
            previous_result = fabric_trace.evaluate(previous_trace)
            self.assertEqual(previous_result["status"], "verified-complete")

            altered_policy = json.loads((previous_trace / "policy.json").read_text(encoding="utf-8"))
            altered_policy["stages"]["proposal"]["requiredApprovers"] = ["different-approver"]
            (previous_trace / "policy.json").write_text(
                json.dumps(altered_policy), encoding="utf-8"
            )
            policy_status, _, policy_error = self.invoke_main(
                "report", "--trace-dir", previous_trace,
            )
            self.assertEqual(policy_status, 2)
            self.assertIn("policy digest differs", policy_error)

            self.git(repo, "config", "user.email", "trace-lifecycle@example.invalid")
            (repo / "revision-change.txt").write_text("new revision\n", encoding="utf-8")
            self.git(repo, "add", "revision-change.txt")
            self.git(repo, "commit", "-qm", "new implementation revision")
            previous_trace_data, _ = fabric_trace.load_trace(previous_trace)
            next_trace = self.create_trace(
                repo, change_dir, policy_path, simulation=True,
                predecessor=previous_trace_data["traceId"],
            )

            next_result = fabric_trace.evaluate(next_trace)
            self.assertNotEqual(next_result["targetRevision"], previous_result["targetRevision"])
            self.assertEqual(next_result["status"], "incomplete")
            self.assertEqual(next_result["timeline"], [])
            self.assertEqual(
                next_result["predecessorHistory"][0]["traceId"],
                previous_trace_data["traceId"],
            )

    def test_unavailable_github_revalidation_invalidates_cached_complete_evidence(self):
        with tempfile.TemporaryDirectory() as temporary_dir:
            repo, change_dir, policy_path = self.create_repository(
                Path(temporary_dir), github_test_producer=True,
            )
            trace_dir = self.create_trace(repo, change_dir, policy_path, simulation=True)
            self.append_fixture_events(
                trace_dir,
                producer_overrides={
                    "test": {
                        "id": "github-test",
                        "type": "github-actions",
                        "repository": "owner/repo",
                        "workflow": ".github/workflows/ci.yml",
                    }
                },
                provenance_overrides={"test": "provider-verified"},
            )
            self.assertEqual(fabric_trace.evaluate(trace_dir)["status"], "verified-complete")

            with patch.object(
                fabric_trace,
                "gh_api_json",
                side_effect=fabric_trace.TraceError("HTTP 503: provider unavailable"),
            ):
                collection_status, _, _ = self.invoke_main(
                    "collect-github",
                    "--trace-dir", trace_dir,
                    "--repo", "owner/repo",
                    "--pr", "12",
                )

            result = fabric_trace.evaluate(trace_dir)
            test_gate = next(stage for stage in result["stages"] if stage["stage"] == "test")
            self.assertEqual(collection_status, 2)
            self.assertEqual(test_gate["gateStatus"], "failed")
            self.assertEqual(result["status"], "incomplete")
            self.assertTrue(any(
                event["kind"] == "github_collection_error"
                for event in result["timeline"]
            ))

    def create_repository(self, root, *, github_test_producer=False):
        repo = root / "repo"
        repo.mkdir()
        self.git(repo, "init", "-q")
        self.git(repo, "config", "user.email", "trace-lifecycle@example.invalid")
        self.git(repo, "config", "user.name", "Trace Lifecycle Test")
        (repo / ".gitignore").write_text(".fabric-traces/\n", encoding="utf-8")
        change_dir = repo / "openspec" / "changes" / "fixture"
        files = {
            "proposal.md": "Synthetic proposal\n",
            "design.md": "Synthetic design\n",
            "tasks.md": "Synthetic tasks\n",
            "specs/fabric-execution-tracing/spec.md": "Synthetic spec\n",
        }
        for relative_path, content in files.items():
            artifact = change_dir / relative_path
            artifact.parent.mkdir(parents=True, exist_ok=True)
            artifact.write_text(content, encoding="utf-8")
        self.git(repo, "add", ".")
        self.git(repo, "commit", "-qm", "initial fixture revision")

        policy = fabric_trace.load_policy(None)
        for stage in fabric_trace.STAGES:
            policy["stages"][stage]["trustedProducers"] = [
                self.github_producer()
                if stage == "test" and github_test_producer
                else self.local_producer(stage)
            ]
        policy["stages"]["legal"]["allowNotApplicable"] = True
        policy["stages"]["security"]["requiredScanners"] = ["fixture-sast"]
        policy_path = root / "policy.json"
        policy_path.write_text(json.dumps(policy), encoding="utf-8")
        return repo, change_dir, policy_path

    def create_trace(self, repo, change_dir, policy_path, *, simulation, predecessor=None):
        return fabric_trace.initialize(argparse.Namespace(
            repo=str(repo),
            change_dir=str(change_dir),
            output_dir=".fabric-traces",
            policy=str(policy_path),
            predecessor=predecessor,
            simulation=simulation,
        ))

    def append_fixture_events(
        self,
        trace_dir,
        *,
        included_stages=None,
        producer_overrides=None,
        provenance_overrides=None,
    ):
        fixture = copy.deepcopy(self.full_fixture)
        trace, paths = fabric_trace.load_trace(trace_dir)
        included_stages = set(included_stages or fabric_trace.STAGES)
        replacements = {
            "$REVISION": trace["targetRevision"],
            "$PROPOSAL_HASH": self.file_hash(trace, "proposal.md"),
            "$DESIGN_HASH": self.file_hash(trace, "design.md"),
            "$TASKS_HASH": self.file_hash(trace, "tasks.md"),
            "$SPEC_HASH": self.file_hash(
                trace, "specs/fabric-execution-tracing/spec.md"
            ),
        }
        for item in fixture["events"]:
            stage = item["stage"]
            if stage not in included_stages:
                continue
            evidence = self.replace_tokens(item["evidence"], replacements)
            producer = (producer_overrides or {}).get(stage, self.local_producer(stage))
            metadata = {"producer": producer, "evidence": evidence}
            producer_run = evidence.get("producerRun")
            if producer_run:
                metadata["run_id"] = producer_run["runId"]
                metadata["run_attempt"] = producer_run["attempt"]
            fabric_trace.append_event(
                trace,
                paths,
                kind="fixture_evidence_observed",
                stage=stage,
                summary=f"Synthetic evidence for {stage}",
                provenance=(provenance_overrides or {}).get(
                    stage, "collector-observed"
                ),
                status="verified",
                metadata=metadata,
            )

    def file_hash(self, trace, relative_path):
        artifact = Path(trace["repository"]["root"]) / trace["changeDir"] / relative_path
        return hashlib.sha256(artifact.read_bytes()).hexdigest()

    def replace_tokens(self, value, replacements):
        if isinstance(value, dict):
            return {
                key: self.replace_tokens(item, replacements)
                for key, item in value.items()
            }
        if isinstance(value, list):
            return [self.replace_tokens(item, replacements) for item in value]
        if isinstance(value, str):
            return replacements.get(value, value)
        return value

    def local_producer(self, stage):
        return {
            "id": f"fixture-{stage}",
            "type": "local-collector",
            "repository": "local",
        }

    def github_producer(self):
        return {
            "id": "github-test",
            "type": "github-actions",
            "repository": "owner/repo",
            "workflow": ".github/workflows/ci.yml",
        }

    def invoke_main(self, *args):
        with redirect_stdout(io.StringIO()) as stdout, redirect_stderr(
            io.StringIO()
        ) as stderr:
            result = fabric_trace.main(list(map(str, args)))
        return result, stdout.getvalue(), stderr.getvalue()

    def git(self, repo, *args):
        return subprocess.run(
            ["git", "-C", str(repo), *args],
            check=True,
            capture_output=True,
            text=True,
        )


if __name__ == "__main__":
    unittest.main()
