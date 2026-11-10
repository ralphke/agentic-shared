import copy
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import fabric_trace


REVISION = "a" * 40
REFERENCE = {"type": "url", "value": "https://example.invalid/evidence/1"}


def evidence_by_type():
    return {
        "planning-approval": {
            "schemaVersion": 1,
            "evidenceType": "planning-approval",
            "artifactHashes": {"proposal.md": "b" * 64},
            "sourceRevision": REVISION,
            "approval": {"actor": "reviewer", "decision": "approved", "reference": REFERENCE},
        },
        "implementation-validation": {
            "schemaVersion": 1,
            "evidenceType": "implementation-validation",
            "sourceRevision": REVISION,
            "treeHash": REVISION,
            "validationStatus": "passed",
            "taskSummary": "Validated implementation tasks",
            "checks": [{"name": "unit-tests", "status": "passed"}],
        },
        "test-results": {
            "schemaVersion": 1,
            "evidenceType": "test-results",
            "sourceRevision": REVISION,
            "producerRun": {"runId": "run-1", "attempt": 1},
            "tests": {"total": 10, "passed": 10, "failed": 0, "errors": 0},
            "coveragePercent": 85.5,
        },
        "security-findings": {
            "schemaVersion": 1,
            "evidenceType": "security-findings",
            "sourceRevision": REVISION,
            "producerRun": {"runId": "run-2", "attempt": 1},
            "scanners": ["sast"],
            "findings": {"critical": 0, "high": 0, "medium": 0, "low": 0},
        },
        "legal-assessment": {
            "schemaVersion": 1,
            "evidenceType": "legal-assessment",
            "sourceRevision": REVISION,
            "riskLevel": "low",
            "triggers": [],
            "assessment": "No escalation trigger identified",
            "assessor": {"actor": "assessor", "reference": REFERENCE},
        },
        "review-approval": {
            "schemaVersion": 1,
            "evidenceType": "review-approval",
            "sourceRevision": REVISION,
            "reviewer": "reviewer",
            "decision": "approved",
            "reference": REFERENCE,
        },
        "deployment-lineage": {
            "schemaVersion": 1,
            "evidenceType": "deployment-lineage",
            "environment": "staging",
            "artifactId": "artifact-1",
            "sourceRevision": REVISION,
            "deployedRevision": REVISION,
            "lineageVerified": True,
            "result": "succeeded",
        },
        "operations-observation": {
            "schemaVersion": 1,
            "evidenceType": "operations-observation",
            "environment": "staging",
            "artifactId": "artifact-1",
            "sourceRevision": REVISION,
            "observedAt": "2025-01-01T12:00:00Z",
            "observationStatus": "succeeded",
            "sloConfigured": True,
        },
    }


def gate_event(evidence_type, *, evidence=None, status="verified", provenance="collector-observed"):
    metadata = {
        "producer": {
            "id": "test-producer",
            "type": "local-collector",
            "repository": "local",
        },
        "evidence": evidence or evidence_by_type()[evidence_type],
    }
    if evidence_type in {"test-results", "security-findings"}:
        run = metadata["evidence"]["producerRun"]
        metadata["run_id"] = run["runId"]
        metadata["run_attempt"] = run["attempt"]
    return {"status": status, "provenance": provenance, "metadata": metadata}


class TracePolicyTests(unittest.TestCase):
    def test_default_policy_is_complete_but_has_no_trusted_producers(self):
        policy = fabric_trace.load_policy(None)
        self.assertEqual(policy["schemaVersion"], fabric_trace.POLICY_VERSION)
        self.assertEqual(policy["evidenceVersion"], fabric_trace.EVIDENCE_VERSION)
        self.assertEqual(set(policy["stages"]), set(fabric_trace.STAGES))
        for stage, contract in policy["stages"].items():
            self.assertEqual(contract["requiredEvidence"], sorted(fabric_trace.STAGE_EVIDENCE_TYPES[stage]))
            self.assertEqual(contract["trustedProducers"], [])

    def test_valid_typed_evidence_for_every_stage_is_accepted(self):
        evidence = evidence_by_type()
        for stage, types in fabric_trace.STAGE_EVIDENCE_TYPES.items():
            with self.subTest(stage=stage):
                evidence_type = next(iter(types))
                fabric_trace.validate_evidence(evidence[evidence_type], stage=stage)

    def test_legal_clearance_is_an_allowed_optional_typed_field(self):
        legal = evidence_by_type()["legal-assessment"]
        legal["riskLevel"] = "high"
        legal["clearance"] = {
            "actor": "counsel",
            "decision": "approved",
            "reference": REFERENCE,
        }
        fabric_trace.validate_evidence(legal, stage="legal")

    def test_malformed_evidence_is_rejected(self):
        cases = [
            ("schema version", "test-results", lambda item: item.update(schemaVersion=True)),
            ("artifact digest", "planning-approval", lambda item: item["artifactHashes"].update({"proposal.md": "bad"})),
            ("unsafe artifact path", "planning-approval", lambda item: item["artifactHashes"].update({"..\\secret.md": "b" * 64})),
            ("coverage range", "test-results", lambda item: item.update(coveragePercent=101)),
            ("negative count", "test-results", lambda item: item["tests"].update(failed=-1)),
            ("producer attempt", "security-findings", lambda item: item["producerRun"].update(attempt=0)),
            ("missing scanner value", "security-findings", lambda item: item.update(scanners=[""])),
            ("invalid risk", "legal-assessment", lambda item: item.update(riskLevel="unknown")),
            ("invalid review decision", "review-approval", lambda item: item.update(decision="commented")),
            ("unverified lineage type", "deployment-lineage", lambda item: item.update(lineageVerified="true")),
            ("invalid timestamp", "operations-observation", lambda item: item.update(observedAt="2025-01-01")),
        ]
        stage_for_type = {
            "planning-approval": "proposal",
            "test-results": "test",
            "security-findings": "security",
            "legal-assessment": "legal",
            "review-approval": "review",
            "deployment-lineage": "deploy",
            "operations-observation": "operate",
        }
        for name, evidence_type, mutate in cases:
            with self.subTest(case=name):
                malformed = copy.deepcopy(evidence_by_type()[evidence_type])
                mutate(malformed)
                with self.assertRaises(fabric_trace.TraceError):
                    fabric_trace.validate_evidence(
                        malformed, stage=stage_for_type[evidence_type]
                    )

    def test_evidence_type_must_match_its_stage(self):
        with self.assertRaisesRegex(fabric_trace.TraceError, "not valid for the test stage"):
            fabric_trace.validate_evidence(
                evidence_by_type()["security-findings"], stage="test"
            )

    def test_malformed_policy_and_producer_are_rejected(self):
        policy = fabric_trace.load_policy(None)
        policy["evidenceVersion"] = True
        with self.assertRaises(fabric_trace.TraceError):
            fabric_trace.validate_policy(policy)

        policy = fabric_trace.load_policy(None)
        policy["stages"]["test"]["trustedProducers"] = [
            {"id": "ci", "type": "github-actions", "repository": "owner/repo"}
        ]
        with self.assertRaisesRegex(fabric_trace.TraceError, "workflow"):
            fabric_trace.validate_policy(policy)

    def test_artifact_policy_requires_run_bound_evidence(self):
        policy = fabric_trace.load_policy(None)
        policy["stages"]["review"]["trustedProducers"] = [{
            "id": "ci",
            "type": "github-actions",
            "repository": "owner/repo",
            "workflow": ".github/workflows/ci.yml",
            "evidenceArtifacts": [{
                "artifactName": "approval",
                "archivePath": "evidence/approval.json",
                "evidenceType": "review-approval",
            }],
        }]
        with self.assertRaisesRegex(fabric_trace.TraceError, "run and attempt provenance"):
            fabric_trace.validate_policy(policy)

    def test_selected_artifacts_are_scoped_to_repository_and_workflow(self):
        policy = fabric_trace.load_policy(None)
        producer = {
            "id": "ci",
            "type": "github-actions",
            "repository": "owner/repo",
            "workflow": ".github/workflows/ci.yml",
            "evidenceArtifacts": [{
                "artifactName": "results",
                "archivePath": "evidence/results.json",
                "evidenceType": "test-results",
            }],
        }
        policy["stages"]["test"]["trustedProducers"] = [producer]

        self.assertEqual(
            set(fabric_trace.selected_evidence_artifacts(
                policy, "OWNER/REPO", ".github/workflows/ci.yml"
            )),
            {"results"},
        )
        self.assertEqual(
            fabric_trace.selected_evidence_artifacts(
                policy, "other/repo", ".github/workflows/ci.yml"
            ),
            {},
        )
        self.assertEqual(
            fabric_trace.selected_evidence_artifacts(
                policy, "owner/repo", ".github/workflows/other.yml"
            ),
            {},
        )

    def test_malformed_nested_evidence_is_rejected_during_event_validation(self):
        event = {
            "schemaVersion": fabric_trace.EVENT_VERSION,
            "eventId": "00000000-0000-4000-8000-000000000001",
            "traceId": "00000000-0000-4000-8000-000000000002",
            "timestamp": fabric_trace.utc_now(),
            "kind": "stage_claim",
            "stage": "test",
            "provenance": "self-reported",
            "summary": "Test evidence",
            "targetRevision": REVISION,
            "metadata": {
                "evidence": {
                    **evidence_by_type()["test-results"],
                    "coveragePercent": "85",
                }
            },
        }
        trace = {"traceId": event["traceId"], "targetRevision": REVISION}
        with self.assertRaisesRegex(fabric_trace.TraceError, "coveragePercent"):
            fabric_trace.validate_event(event, trace)

    def test_labels_checked_tasks_and_green_jobs_do_not_replace_typed_evidence(self):
        contract = {
            "requiredEvidence": ["test-results"],
            "trustedProducers": [{
                "id": "test-producer",
                "type": "local-collector",
                "repository": "local",
            }],
        }
        event = {
            **gate_event("test-results"),
            "metadata": {"evidenceType": "test-results", "label": "passed", "tasksChecked": True},
        }
        state, reasons = fabric_trace.evaluate_stage("test", [event], contract, REVISION)
        self.assertEqual(state, "missing")
        self.assertIn("missing required typed evidence", reasons[0])

    def test_unconfigured_producer_and_untrusted_provenance_fail_closed(self):
        event = gate_event("test-results")
        state, reasons = fabric_trace.evaluate_stage(
            "test", [event], {"requiredEvidence": ["test-results"], "trustedProducers": []}, REVISION
        )
        self.assertEqual(state, "unverified")
        self.assertIn("no trusted evidence producer", reasons[0])

        contract = {
            "requiredEvidence": ["test-results"],
            "trustedProducers": [{
                "id": "test-producer",
                "type": "local-collector",
                "repository": "local",
            }],
        }
        event["provenance"] = "self-reported"
        self.assertEqual(fabric_trace.evaluate_stage("test", [event], contract, REVISION)[0], "unverified")

    def test_test_coverage_below_threshold_fails_gate(self):
        evidence = evidence_by_type()["test-results"]
        evidence["coveragePercent"] = 79.9
        contract = {
            "requiredEvidence": ["test-results"],
            "trustedProducers": [{
                "id": "test-producer",
                "type": "local-collector",
                "repository": "local",
            }],
        }
        state, reasons = fabric_trace.evaluate_stage(
            "test", [gate_event("test-results", evidence=evidence)], contract, REVISION
        )
        self.assertEqual(state, "failed")
        self.assertIn("at least 80%", reasons[0])

    def test_missing_required_security_scanner_and_high_findings_fail_gate(self):
        contract = {
            "requiredEvidence": ["security-findings"],
            "requiredScanners": ["sast", "dependency"],
            "trustedProducers": [{
                "id": "test-producer",
                "type": "local-collector",
                "repository": "local",
            }],
        }
        evidence = evidence_by_type()["security-findings"]
        state, reasons = fabric_trace.evaluate_stage(
            "security", [gate_event("security-findings", evidence=evidence)], contract, REVISION
        )
        self.assertEqual(state, "failed")
        self.assertIn("dependency", reasons[0])

        evidence["scanners"].append("dependency")
        evidence["findings"]["critical"] = 1
        state, reasons = fabric_trace.evaluate_stage(
            "security", [gate_event("security-findings", evidence=evidence)], contract, REVISION
        )
        self.assertEqual(state, "failed")
        self.assertIn("CRITICAL", reasons[0])

    def test_high_risk_legal_assessment_requires_clearance(self):
        evidence = evidence_by_type()["legal-assessment"]
        evidence["riskLevel"] = "high"
        evidence["triggers"] = ["regulatory"]
        contract = {
            "requiredEvidence": ["legal-assessment"],
            "trustedProducers": [{
                "id": "test-producer",
                "type": "local-collector",
                "repository": "local",
            }],
        }
        state, reasons = fabric_trace.evaluate_stage(
            "legal", [gate_event("legal-assessment", evidence=evidence)], contract, REVISION
        )
        self.assertEqual(state, "failed")
        self.assertIn("requires explicit clearance", reasons[0])

    def test_low_risk_legal_assessment_is_not_applicable_only_when_policy_allows_it(self):
        contract = {
            "requiredEvidence": ["legal-assessment"],
            "trustedProducers": [{
                "id": "test-producer",
                "type": "local-collector",
                "repository": "local",
            }],
            "allowNotApplicable": True,
        }
        state, reasons = fabric_trace.evaluate_stage(
            "legal", [gate_event("legal-assessment")], contract, REVISION
        )
        self.assertEqual(state, "not-applicable")
        self.assertEqual(reasons, [])

    def test_planning_approval_is_stale_when_artifact_content_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            change_dir = Path(directory)
            artifact = change_dir / "proposal.md"
            artifact.write_text("original proposal", encoding="utf-8")
            expected_hash = hashlib.sha256(artifact.read_bytes()).hexdigest()
            artifact.write_text("updated proposal", encoding="utf-8")
            evidence = copy.deepcopy(evidence_by_type()["planning-approval"])
            evidence["artifactHashes"] = {"proposal.md": expected_hash}
            contract = {
                "requiredEvidence": ["planning-approval"],
                "trustedProducers": [{
                    "id": "test-producer",
                    "type": "local-collector",
                    "repository": "local",
                }],
            }
            state, reasons = fabric_trace.evaluate_stage(
                "proposal",
                [gate_event("planning-approval", evidence=evidence)],
                contract,
                REVISION,
                change_dir=change_dir,
            )
        self.assertEqual(state, "stale")
        self.assertIn("current artifact hashes", reasons[0])

    def test_local_evidence_is_stale_after_dirty_implementation_command(self):
        evidence_event = gate_event("test-results")
        evidence_event.update(eventId="test-evidence", stage="test")
        command_event = {
            "eventId": "later-command",
            "stage": "implement",
            "kind": "command_completed",
            "metadata": {"workspaceDirtyAtCompletion": True, "targetMatches": True},
        }
        contract = {
            "requiredEvidence": ["test-results"],
            "trustedProducers": [{
                "id": "test-producer",
                "type": "local-collector",
                "repository": "local",
            }],
        }
        state, reasons = fabric_trace.evaluate_stage(
            "test",
            [evidence_event],
            contract,
            REVISION,
            all_events=[evidence_event, command_event],
        )
        self.assertEqual(state, "stale")
        self.assertIn("subsequently changed workspace", reasons[0])

    def test_successful_rerun_does_not_hide_failure_from_another_run(self):
        failed = gate_event("test-results")
        failed["metadata"]["evidence"]["producerRun"] = {"runId": "failed-run", "attempt": 1}
        failed["metadata"].update(run_id="failed-run", run_attempt=1)
        successful = gate_event("test-results")
        successful["metadata"]["evidence"]["producerRun"] = {"runId": "success-run", "attempt": 1}
        successful["metadata"].update(run_id="success-run", run_attempt=1)
        failed["status"] = "failed"
        contract = {
            "requiredEvidence": ["test-results"],
            "trustedProducers": [{
                "id": "test-producer",
                "type": "local-collector",
                "repository": "local",
            }],
        }
        state, reasons = fabric_trace.evaluate_stage(
            "test", [failed, successful], contract, REVISION
        )
        self.assertEqual(state, "failed")
        self.assertIn("event failed", reasons[0])

    def test_successful_attempt_supersedes_same_run_failure_without_deleting_history(self):
        failed = gate_event("test-results")
        failed["metadata"]["evidence"]["producerRun"] = {"runId": "same-run", "attempt": 1}
        failed["metadata"].update(run_id="same-run", run_attempt=1)
        failed["status"] = "failed"
        successful = gate_event("test-results")
        successful["metadata"]["evidence"]["producerRun"] = {"runId": "same-run", "attempt": 2}
        successful["metadata"].update(run_id="same-run", run_attempt=2)
        events = [failed, successful]
        selected = fabric_trace.effective_evidence_events(events, "test-results")
        self.assertEqual(len(events), 2)
        self.assertEqual(selected, [successful])

    def test_prerequisite_ordering_rejects_deployment_before_review(self):
        policy = fabric_trace.load_policy(None)
        order = [
            "proposal", "design", "implement", "test", "security",
            "legal", "deploy", "review", "operate",
        ]
        events = []
        for index, stage in enumerate(order):
            evidence_type = next(iter(fabric_trace.STAGE_EVIDENCE_TYPES[stage]))
            evidence = copy.deepcopy(evidence_by_type()[evidence_type])
            events.append({
                "eventId": f"event-{index}",
                "stage": stage,
                "metadata": {"evidence": evidence},
            })
        stages = [
            {
                "stage": stage,
                "gateStatus": "verified",
                "reasons": [],
            }
            for stage in fabric_trace.STAGES
        ]
        fabric_trace.apply_prerequisite_ordering(stages, events, policy)
        result = next(stage for stage in stages if stage["stage"] == "deploy")
        self.assertEqual(result["gateStatus"], "unverified")
        self.assertIn("review evidence must precede deployment", result["reasons"][0])

    def test_operations_evidence_must_match_deployed_artifact(self):
        policy = fabric_trace.load_policy(None)
        events = []
        for index, stage in enumerate(fabric_trace.STAGES):
            evidence_type = next(iter(fabric_trace.STAGE_EVIDENCE_TYPES[stage]))
            evidence = copy.deepcopy(evidence_by_type()[evidence_type])
            if stage == "operate":
                evidence["artifactId"] = "different-artifact"
            events.append({
                "eventId": f"event-{index}",
                "stage": stage,
                "metadata": {"evidence": evidence},
            })
        stages = [
            {
                "stage": stage,
                "gateStatus": "verified",
                "reasons": [],
            }
            for stage in fabric_trace.STAGES
        ]
        fabric_trace.apply_prerequisite_ordering(stages, events, policy)
        result = next(stage for stage in stages if stage["stage"] == "operate")
        self.assertEqual(result["gateStatus"], "stale")
        self.assertIn("does not match", result["reasons"][0])

    def test_predecessor_history_reports_prior_trace_events(self):
        repository = {"root": "C:\\repo", "origin": "local"}
        current = {
            "traceId": "current",
            "repository": repository,
            "changeDir": "openspec/changes/example",
            "predecessorTraceId": "previous",
        }
        previous = {
            "traceId": "previous",
            "repository": repository,
            "changeDir": "openspec/changes/example",
            "targetRevision": REVISION,
            "createdAt": "2025-01-01T00:00:00Z",
            "predecessorTraceId": None,
        }
        with (
            patch.object(fabric_trace, "load_trace", return_value=(previous, {"events": Path("events.jsonl")})),
            patch.object(fabric_trace, "read_events", return_value=[{"eventId": "one"}]),
        ):
            history = fabric_trace.predecessor_history(current, Path("C:\\repo"))
        self.assertEqual(history[0]["traceId"], "previous")
        self.assertEqual(history[0]["eventCount"], 1)


if __name__ == "__main__":
    unittest.main()
