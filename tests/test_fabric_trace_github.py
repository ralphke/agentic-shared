import argparse
import io
import json
import subprocess
import tempfile
import unittest
import zipfile
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from scripts import fabric_trace


class TraceGitHubCollectionTests(unittest.TestCase):
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
        self.revision = self.git("rev-parse", "HEAD").stdout.strip()
        change = self.repo / "openspec" / "changes" / "first"
        change.mkdir(parents=True)
        self.trace_dir = fabric_trace.initialize(argparse.Namespace(
            repo=str(self.repo),
            change_dir=str(change),
            output_dir=".fabric-traces",
            policy=None,
            predecessor=None,
            simulation=False,
        ))
        self.args = argparse.Namespace(
            trace_dir=str(self.trace_dir),
            repo="owner/repo",
            pr=12,
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def git(self, *args):
        return subprocess.run(
            ["git", "-C", str(self.repo), *args],
            check=True,
            capture_output=True,
            text=True,
        )

    def events(self):
        trace, paths = fabric_trace.load_trace(self.trace_dir)
        return fabric_trace.read_events(trace, paths["events"])

    def collect(self, responses):
        with patch.object(fabric_trace, "gh_api_json", side_effect=responses):
            return fabric_trace.command_collect_github(self.args)

    def configure_selected_artifact(self):
        policy = fabric_trace.load_policy(None)
        policy["stages"]["test"]["requiredEvidence"] = ["test-results"]
        policy["stages"]["test"]["trustedProducers"] = [{
            "id": "ci",
            "type": "github-actions",
            "repository": "owner/repo",
            "workflow": ".github/workflows/ci.yml",
            "evidenceArtifacts": [{
                "artifactName": "results",
                "archivePath": "evidence/results.json",
                "evidenceType": "test-results",
            }],
        }]
        (self.trace_dir / "policy.json").write_text(
            json.dumps(policy), encoding="utf-8"
        )
        trace, paths = fabric_trace.load_trace(self.trace_dir)
        trace["policyDigest"] = fabric_trace.digest_json(policy)
        fabric_trace.atomic_write(
            paths["metadata"], fabric_trace.canonical_json(trace) + b"\n"
        )

    def configure_deployment_producer(self):
        policy = fabric_trace.load_policy(None)
        policy["stages"]["deploy"]["trustedProducers"] = [{
            "id": "production-deployer",
            "type": "github-deployment",
            "repository": "owner/repo",
            "environment": "staging",
        }]
        (self.trace_dir / "policy.json").write_text(
            json.dumps(policy), encoding="utf-8"
        )

    def artifact_responses(self, artifact, evidence):
        responses = self.base_responses() + [
            [{"id": 100, "run_attempt": 1, "head_sha": self.revision,
              "conclusion": "failure", "path": ".github/workflows/ci.yml"}],
            [{"jobs": []}],
            [{"id": 100, "run_attempt": 2, "head_sha": self.revision,
              "conclusion": "success", "path": ".github/workflows/ci.yml"}],
            [{"jobs": []}],
            [{"artifacts": [artifact] if artifact is not None else []}],
            [{"id": 201, "state": "success"}],
        ]
        return responses

    def evidence_archive(self, evidence, *, path="evidence/results.json"):
        output = io.BytesIO()
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr(path, json.dumps(evidence))
        return output.getvalue()

    def valid_test_evidence(self):
        return {
            "schemaVersion": 1,
            "evidenceType": "test-results",
            "sourceRevision": self.revision,
            "producerRun": {"runId": "100", "attempt": 2},
            "tests": {"total": 10, "passed": 10, "failed": 0, "errors": 0},
            "coveragePercent": 85.5,
        }

    def base_responses(self, *, head_repo="owner/repo", head=None):
        return [
            [{"head": {"repo": {"full_name": head_repo}, "sha": head or self.revision}}],
            [{"workflow_runs": [
                {
                    "id": 100,
                    "run_attempt": 2,
                    "head_sha": self.revision,
                    "path": ".github/workflows/ci.yml",
                    "html_url": "https://github.com/owner/repo/actions/runs/100",
                },
                {
                    "id": 100,
                    "run_attempt": 2,
                    "head_sha": self.revision,
                    "path": ".github/workflows/ci.yml",
                },
            ]}],
            [[
                {"id": 1, "user": {"login": "reviewer"}, "state": "APPROVED",
                 "submitted_at": "2025-01-01T00:00:00Z", "commit_id": self.revision},
                {"id": 2, "user": {"login": "reviewer"}, "state": "DISMISSED",
                 "submitted_at": "2025-01-02T00:00:00Z", "commit_id": self.revision},
                {"id": 3, "user": {"login": "blocker"}, "state": "CHANGES_REQUESTED",
                 "submitted_at": "2025-01-03T00:00:00Z", "commit_id": self.revision},
            ]],
            [{"id": 200, "environment": "staging", "sha": self.revision,
              "url": "https://api.github.com/repos/owner/repo/deployments/200"}],
        ]

    def test_collects_all_attempts_steps_artifacts_and_deployment_statuses(self):
        responses = self.base_responses() + [
            [{"id": 100, "run_attempt": 1, "head_sha": self.revision,
              "conclusion": "failure", "path": ".github/workflows/ci.yml"}],
            [{"jobs": [
                {"id": 11, "name": "test", "conclusion": "failure",
                 "steps": [
                     {"number": 1, "name": "Skipped step", "conclusion": "skipped"},
                     {"number": 2, "name": "Cancelled step", "conclusion": "cancelled"},
                 ]},
                {"id": 12, "name": "test", "conclusion": "success",
                 "steps": [{"number": 1, "name": "Passed step", "conclusion": "success"}]},
            ]}],
            [{"id": 100, "run_attempt": 2, "head_sha": self.revision,
              "conclusion": "success", "path": ".github/workflows/ci.yml"}],
            [{"jobs": [{"id": 21, "name": "test", "conclusion": "success",
                        "steps": [{"number": 1, "name": "Passed step", "conclusion": "success"}]}]}],
            [{"artifacts": [{"id": 300, "name": "results", "size_in_bytes": 42,
                             "expired": False, "url": "https://api.github.com/artifacts/300"}]}],
            [{"id": 201, "state": "success", "target_url": "https://example.invalid/deploy"}],
        ]
        with patch.object(fabric_trace, "gh_api_json", side_effect=responses) as api:
            self.assertEqual(fabric_trace.command_collect_github(self.args), 0)

        events = self.events()
        kinds = [event["kind"] for event in events]
        self.assertEqual(kinds.count("github_attempt_observed"), 2)
        self.assertEqual(kinds.count("github_job_observed"), 3)
        self.assertEqual(kinds.count("github_step_observed"), 4)
        self.assertEqual(kinds.count("github_artifact_observed"), 1)
        self.assertEqual(kinds.count("github_deployment_status_observed"), 1)
        self.assertEqual(kinds.count("github_review_observed"), 2)
        self.assertEqual(
            {(event["metadata"]["job_id"], event["summary"].split(" — ")[0])
             for event in events if event["kind"] == "github_job_observed"},
            {("11", "test"), ("12", "test"), ("21", "test")},
        )
        skipped, cancelled = [
            event for event in events
            if event["kind"] == "github_step_observed"
            and event["metadata"]["step_name"] in {"Skipped step", "Cancelled step"}
        ]
        self.assertEqual(skipped["status"], "unverified")
        self.assertEqual(cancelled["status"], "unverified")
        reviews = {event["metadata"]["reviewer"]: event for event in events
                   if event["kind"] == "github_review_observed"}
        self.assertEqual(reviews["reviewer"]["metadata"]["state"], "DISMISSED")
        self.assertEqual(reviews["reviewer"]["status"], "unverified")
        self.assertEqual(reviews["blocker"]["status"], "failed")
        self.assertTrue(all(call.kwargs.get("paginate", False) for call in api.call_args_list
                            if "runs?" in call.args[0] or "reviews" in call.args[0]
                            or "deployments" in call.args[0] or "jobs" in call.args[0]
                            or "artifacts" in call.args[0]))

    def test_different_deployment_revision_is_verified_when_github_confirms_lineage(self):
        self.configure_deployment_producer()
        deployed_revision = "b" * 40
        responses = [
            [{"head": {
                "repo": {"full_name": "owner/repo"},
                "sha": self.revision,
            }, "merge_commit_sha": deployed_revision}],
            [{"workflow_runs": []}],
            [[]],
            [{"id": 200, "environment": "staging", "sha": self.revision}],
            [{"id": 201, "environment": "staging", "sha": deployed_revision}],
            [{"id": 301, "state": "success"}],
            [{"id": 302, "state": "success"}],
            [{"status": "ahead", "merge_base_commit": {"sha": self.revision}}],
        ]
        with patch.object(fabric_trace, "gh_api_json", side_effect=responses) as api:
            self.assertEqual(fabric_trace.command_collect_github(self.args), 0)

        lineage = [
            event for event in self.events()
            if event["kind"] == "github_deployment_lineage_observed"
        ]
        self.assertEqual(len(lineage), 2)
        verified = next(
            event for event in lineage
            if event["metadata"]["evidence"]["deployedRevision"] == deployed_revision
        )
        self.assertTrue(verified["metadata"]["evidence"]["lineageVerified"])
        self.assertEqual(verified["status"], "verified")
        self.assertEqual(
            fabric_trace.evaluate_stage(
                "deploy", [verified],
                fabric_trace.load_policy(self.trace_dir / "policy.json")["stages"]["deploy"],
                self.revision,
            )[0],
            "verified",
        )
        self.assertTrue(any(
            f"/compare/{self.revision}...{deployed_revision}" in call.args[0]
            for call in api.call_args_list
        ))

    def test_unrelated_successful_deployment_remains_unverified(self):
        self.configure_deployment_producer()
        unrelated_revision = "c" * 40
        responses = [
            [{"head": {
                "repo": {"full_name": "owner/repo"},
                "sha": self.revision,
            }, "merge_commit_sha": unrelated_revision}],
            [{"workflow_runs": []}],
            [[]],
            [[]],
            [{"id": 202, "environment": "staging", "sha": unrelated_revision}],
            [{"id": 303, "state": "success"}],
            [{
                "status": "diverged",
                "merge_base_commit": {"sha": "d" * 40},
            }],
        ]
        with patch.object(fabric_trace, "gh_api_json", side_effect=responses):
            self.assertEqual(fabric_trace.command_collect_github(self.args), 0)

        lineage = next(
            event for event in self.events()
            if event["kind"] == "github_deployment_lineage_observed"
        )
        self.assertFalse(lineage["metadata"]["evidence"]["lineageVerified"])
        self.assertEqual(lineage["status"], "unverified")
        state, reasons = fabric_trace.evaluate_stage(
            "deploy",
            [lineage],
            fabric_trace.load_policy(self.trace_dir / "policy.json")["stages"]["deploy"],
            self.revision,
        )
        self.assertEqual(state, "unverified")
        self.assertTrue(reasons)

    def test_fork_head_is_rejected_and_collection_error_is_persisted(self):
        responses = self.base_responses(head_repo="someone/fork")
        with patch.object(fabric_trace, "gh_api_json", side_effect=responses):
            with self.assertRaisesRegex(fabric_trace.TraceError, "repository mismatch"):
                fabric_trace.command_collect_github(self.args)
        self.assertEqual(self.events()[-1]["kind"], "github_collection_error")

    def test_stale_pull_request_head_is_rejected(self):
        responses = self.base_responses(head="b" * 40)
        with patch.object(fabric_trace, "gh_api_json", side_effect=responses):
            with self.assertRaisesRegex(fabric_trace.TraceError, "revision mismatch"):
                fabric_trace.command_collect_github(self.args)
        self.assertEqual(self.events()[-1]["kind"], "github_collection_error")

    def test_attempt_with_stale_sha_is_rejected(self):
        responses = self.base_responses() + [
            [{"id": 100, "run_attempt": 1, "head_sha": "b" * 40}],
        ]
        with patch.object(fabric_trace, "gh_api_json", side_effect=responses):
            with self.assertRaisesRegex(fabric_trace.TraceError, "does not match"):
                fabric_trace.command_collect_github(self.args)
        self.assertEqual(self.events()[-1]["kind"], "github_collection_error")

    def test_ingests_only_selected_artifact_with_matching_run_and_attempt_provenance(self):
        self.configure_selected_artifact()
        artifact = {"id": 300, "name": "results", "size_in_bytes": 512, "expired": False}
        responses = self.artifact_responses(artifact, self.valid_test_evidence())
        with (
            patch.object(fabric_trace, "gh_api_json", side_effect=responses),
            patch.object(
                fabric_trace, "gh_api_bytes",
                return_value=self.evidence_archive(self.valid_test_evidence()),
            ) as download,
        ):
            self.assertEqual(fabric_trace.command_collect_github(self.args), 0)

        event = next(event for event in self.events()
                     if event["kind"] == "github_artifact_evidence_observed")
        self.assertEqual(event["provenance"], "provider-verified")
        self.assertEqual(event["status"], "verified")
        self.assertEqual(event["metadata"]["run_id"], "100")
        self.assertEqual(event["metadata"]["run_attempt"], 2)
        self.assertEqual(event["metadata"]["evidence"], self.valid_test_evidence())
        download.assert_called_once_with(
            "/repos/owner/repo/actions/artifacts/300/zip"
        )

    def test_expired_and_missing_selected_artifacts_are_rejected_without_download(self):
        self.configure_selected_artifact()
        cases = [
            ({"id": 300, "name": "results", "size_in_bytes": 512, "expired": True}, "expired"),
            (None, "missing"),
        ]
        for artifact, expected in cases:
            with self.subTest(expected=expected):
                responses = self.artifact_responses(artifact, None)
                with (
                    patch.object(fabric_trace, "gh_api_json", side_effect=responses),
                    patch.object(fabric_trace, "gh_api_bytes") as download,
                ):
                    self.assertEqual(fabric_trace.command_collect_github(self.args), 0)
                rejected = [event for event in self.events()
                            if event["kind"] == "github_artifact_evidence_rejected"]
                self.assertIn(expected, rejected[-1]["summary"])
                download.assert_not_called()

    def test_wrong_attempt_and_stale_revision_artifacts_are_not_accepted(self):
        self.configure_selected_artifact()
        wrong_attempt = self.valid_test_evidence()
        wrong_attempt["producerRun"]["attempt"] = 1
        stale_revision = self.valid_test_evidence()
        stale_revision["sourceRevision"] = "b" * 40
        for evidence, expected in (
            (wrong_attempt, "does not match the collected run attempt"),
            (stale_revision, "different revision"),
        ):
            with self.subTest(expected=expected):
                artifact = {
                    "id": 300, "name": "results", "size_in_bytes": 512, "expired": False,
                }
                responses = self.artifact_responses(artifact, evidence)
                with (
                    patch.object(fabric_trace, "gh_api_json", side_effect=responses),
                    patch.object(
                        fabric_trace, "gh_api_bytes",
                        return_value=self.evidence_archive(evidence),
                    ),
                ):
                    self.assertEqual(fabric_trace.command_collect_github(self.args), 0)
                rejected = [event for event in self.events()
                            if event["kind"] == "github_artifact_evidence_rejected"]
                self.assertIn(expected, rejected[-1]["summary"])
                self.assertEqual(rejected[-1]["provenance"], "collector-observed")

    def test_malformed_and_unsafe_artifact_archives_fail_closed(self):
        evidence = self.valid_test_evidence()
        for archive_bytes, expected in (
            (b"not a zip archive", "not a valid ZIP archive"),
            (self.evidence_archive(evidence, path="../results.json"), "safe relative"),
        ):
            with self.subTest(expected=expected):
                with self.assertRaisesRegex(fabric_trace.TraceError, expected):
                    fabric_trace.parse_evidence_artifact(
                        archive_bytes, "evidence/results.json"
                    )

    def test_oversized_artifacts_and_members_are_rejected(self):
        oversized_archive = b"x" * (fabric_trace.MAX_EVIDENCE_ARTIFACT_BYTES + 1)
        with self.assertRaisesRegex(fabric_trace.TraceError, "archive exceeds"):
            fabric_trace.parse_evidence_artifact(
                oversized_archive, "evidence/results.json"
            )

        output = io.BytesIO()
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr(
                "evidence/results.json",
                b"x" * (fabric_trace.MAX_EVIDENCE_MEMBER_BYTES + 1),
            )
        with self.assertRaisesRegex(fabric_trace.TraceError, "member exceeds"):
            fabric_trace.parse_evidence_artifact(
                output.getvalue(), "evidence/results.json"
            )

    def test_local_self_reported_evidence_cannot_satisfy_provider_contract(self):
        evidence = self.valid_test_evidence()
        event = {
            "schemaVersion": fabric_trace.EVENT_VERSION,
            "eventId": "00000000-0000-4000-8000-000000000001",
            "traceId": "00000000-0000-4000-8000-000000000002",
            "timestamp": fabric_trace.utc_now(),
            "kind": "stage_claim",
            "stage": "test",
            "provenance": "self-reported",
            "summary": "Locally supplied test evidence",
            "targetRevision": self.revision,
            "metadata": {"evidenceType": "test-results", "evidence": evidence},
        }
        contract = {
            "requiredEvidence": ["test-results"],
            "trustedProducers": [{
                "id": "ci",
                "type": "github-actions",
                "repository": "owner/repo",
                "workflow": ".github/workflows/ci.yml",
            }],
        }
        state, reasons = fabric_trace.evaluate_stage(
            "test", [event], contract, self.revision
        )
        self.assertEqual(state, "unverified")
        self.assertIn("trusted producer", reasons[0])

    def test_paginated_gh_response_uses_slurp_and_normalizes_pages(self):
        result = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout='[[{"id": 1}], [{"id": 2}]]',
            stderr="",
        )
        with patch.object(fabric_trace.subprocess, "run", return_value=result) as run:
            pages = fabric_trace.gh_api_json("/repos/owner/repo/issues", paginate=True)
        self.assertEqual(pages, [[{"id": 1}], [{"id": 2}]])
        command = run.call_args.args[0]
        self.assertIn("--paginate", command)
        self.assertIn("--slurp", command)
        self.assertIn("--method", command)
        self.assertEqual(command[command.index("--method") + 1], "GET")

    def test_documented_collect_github_cli_command_works_with_mocked_api(self):
        with (
            patch.object(
                fabric_trace, "gh_api_json",
                side_effect=self.artifact_responses(None, None),
            ),
            redirect_stdout(io.StringIO()),
        ):
            collect_result = fabric_trace.main([
                "collect-github",
                "--trace-dir", str(self.trace_dir),
                "--repo", "owner/repo",
                "--pr", "12",
            ])
            report_result = fabric_trace.main([
                "report", "--trace-dir", str(self.trace_dir),
            ])
            with redirect_stderr(io.StringIO()):
                check_result = fabric_trace.main([
                    "check", "--trace-dir", str(self.trace_dir),
                ])

        self.assertEqual(collect_result, 0)
        self.assertEqual(report_result, 0)
        self.assertNotEqual(check_result, 0)

    def test_collection_failures_are_persisted_and_return_nonzero(self):
        failures = (
            (fabric_trace.TraceError("HTTP 401: authentication required"), "authentication"),
            (fabric_trace.TraceError("HTTP 403: forbidden"), "authorization"),
            (OSError("network is unavailable"), "network"),
            (IndexError("unexpected empty response"), "schema"),
            (subprocess.SubprocessError("gh process failed"), "subprocess"),
        )
        for error, label in failures:
            with self.subTest(failure=label):
                with (
                    patch.object(fabric_trace, "gh_api_json", side_effect=error),
                    redirect_stderr(io.StringIO()),
                ):
                    result = fabric_trace.main([
                        "collect-github",
                        "--trace-dir", str(self.trace_dir),
                        "--repo", "owner/repo",
                        "--pr", "12",
                    ])
                self.assertNotEqual(result, 0)
                failure = self.events()[-1]
                self.assertEqual(failure["kind"], "github_collection_error")
                self.assertEqual(failure["status"], "failed")

    def test_collection_failure_invalidates_previously_verified_evidence(self):
        self.configure_selected_artifact()
        artifact = {"id": 300, "name": "results", "size_in_bytes": 512, "expired": False}
        responses = self.artifact_responses(artifact, self.valid_test_evidence())
        with (
            patch.object(fabric_trace, "gh_api_json", side_effect=responses),
            patch.object(
                fabric_trace, "gh_api_bytes",
                return_value=self.evidence_archive(self.valid_test_evidence()),
            ),
        ):
            self.assertEqual(fabric_trace.command_collect_github(self.args), 0)

        self.assertEqual(
            next(event for event in self.events()
                 if event["kind"] == "github_artifact_evidence_observed")["status"],
            "verified",
        )
        with (
            patch.object(
                fabric_trace, "gh_api_json",
                side_effect=fabric_trace.TraceError("HTTP 403: forbidden"),
            ),
            redirect_stderr(io.StringIO()),
        ):
            self.assertNotEqual(fabric_trace.main([
                "collect-github",
                "--trace-dir", str(self.trace_dir),
                "--repo", "owner/repo",
                "--pr", "12",
            ]), 0)
        test_gate = next(
            stage for stage in fabric_trace.evaluate(self.trace_dir)["stages"]
            if stage["stage"] == "test"
        )
        self.assertEqual(test_gate["gateStatus"], "failed")

    def test_github_api_helpers_only_issue_get_requests(self):
        calls = []

        def run(command, **kwargs):
            calls.append(command)
            if "--output" in command:
                Path(command[command.index("--output") + 1]).write_bytes(b"archive")
            return subprocess.CompletedProcess(command, 0, stdout="{}", stderr="")

        with patch.object(fabric_trace.subprocess, "run", side_effect=run):
            self.assertEqual(fabric_trace.gh_api_json("/repos/owner/repo"), [{}])
            self.assertEqual(
                fabric_trace.gh_api_bytes("/repos/owner/repo/actions/artifacts/1/zip"),
                b"archive",
            )

        self.assertEqual(len(calls), 2)
        for command in calls:
            self.assertEqual(command[command.index("--method") + 1], "GET")
            self.assertFalse(any(
                method in command for method in ("POST", "PATCH", "PUT", "DELETE")
            ))


if __name__ == "__main__":
    unittest.main()
