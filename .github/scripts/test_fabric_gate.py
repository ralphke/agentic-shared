"""Revision, lifecycle, provenance and control regression tests; no network."""

import copy
import importlib
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / ".github/skills/fabric-verify-change/scripts"
sys.path.insert(0, str(RUNTIME))
COLLECTOR = importlib.import_module("collect_fabric_evidence")
EVALUATOR = importlib.import_module("fabric_gate")
CONTROL = importlib.import_module("run_fabric_gate_control")
Collector, GitHubAPI = COLLECTOR.Collector, COLLECTOR.GitHubAPI
preflight, trusted_checkout = COLLECTOR.preflight, COLLECTOR.trusted_checkout
GateError, evaluate = EVALUATOR.GateError, EVALUATOR.evaluate
fresh, load_json = EVALUATOR.fresh, EVALUATOR.load_json
required_gates = EVALUATOR.required_gates
validate_config, validate_manifest = EVALUATOR.validate_config, EVALUATOR.validate_manifest
merge_control, release_control = CONTROL.merge_control, CONTROL.release_control
release_snapshot = CONTROL.release_snapshot
POLICY_PATH = RUNTIME / "gate-policy.json"
REPOSITORY = "ralphke/agentic-shared"
REVISION = "a" * 40
BASE_REVISION = "b" * 40
OTHER_REVISION = "c" * 40
OBSERVED = "2026-11-07T12:00:00Z"
NOW = datetime(2026, 11, 7, 12, 5, tzinfo=UTC)
APP_ID = 12345


def configured_policy():
    """Fixtures replace deliberately unconfigured administrator identities."""
    config = load_json(POLICY_PATH.read_text(encoding="utf-8"))
    config["control"] = {"app_id": APP_ID, "reviewer_ids": [10],
        "custody_source": {"kind": "check", "app_id": APP_ID + 1, "name": "Custody certification"}}
    for gates in config["lifecycles"].values():
        for rule in gates.values():
            source = rule["source"]
            if source["kind"] == "check":
                source["app_id"] = APP_ID
            else:
                source["creator_id"] = 42
                source["status_creator_id"] = 43
    return config


def check_record(identifier, name, revision_sha=REVISION):
    """Authorized check produced by a dedicated non-Actions application."""
    return {"id": identifier, "name": name, "head_sha": revision_sha,
            "app": {"id": APP_ID, "slug": "trusted-evidence-app"},
            "status": "completed", "conclusion": "success", "completed_at": OBSERVED,
            "output": {"summary": ""}}


class FixtureAPI:
    """Model authenticated API records, including current PR and deployment."""

    def __init__(self, config):
        names = {rule["source"]["name"] for gates in config["lifecycles"].values()
                 for rule in gates.values() if rule["source"]["kind"] == "check"}
        self.checks = [check_record(index, name) for index, name in enumerate(sorted(names), 1)]
        self.reviews = []
        self.deployments = [{"id": 80, "sha": REVISION, "environment": "production",
                             "creator": {"id": 42}}]
        self.statuses = [{"id": 81, "state": "success", "environment": "production",
                          "creator": {"id": 43}, "created_at": OBSERVED}]
        self.pull = {"state": "open", "head": {"sha": REVISION}, "user": {"id": 99},
                     "merged": True, "merge_commit_sha": REVISION,
                     "base": {"sha": BASE_REVISION, "ref": "main",
                              "repo": {"full_name": REPOSITORY}}}
        self.calls = []

    def get(self, endpoint):
        self.calls.append(endpoint)
        if endpoint.endswith("/pulls/1"):
            return copy.deepcopy(self.pull)
        if endpoint == f"repos/{REPOSITORY}":
            return {"default_branch": "main"}
        if endpoint.endswith("/commits/main"):
            return {"sha": BASE_REVISION}
        if endpoint.endswith("/branches/main"):
            return {"protected": True, "commit": {"sha": BASE_REVISION}}
        if endpoint.endswith("/releases/1"):
            return {"id": 1, "draft": False, "published_at": OBSERVED, "tag_name": "v1"}
        if endpoint.endswith("/git/ref/tags/v1"):
            return {"object": {"type": "commit", "sha": REVISION}}
        if "/commits/" in endpoint:
            return {"sha": REVISION}
        raise GateError(f"unexpected endpoint: {endpoint}")

    def pages(self, endpoint, field=None):
        self.calls.append(endpoint)
        if "check-runs" in endpoint:
            return copy.deepcopy(self.checks)
        if endpoint.endswith("/reviews"):
            return copy.deepcopy(self.reviews)
        if "/statuses" in endpoint:
            return copy.deepcopy(self.statuses)
        if "/deployments?" in endpoint:
            return copy.deepcopy(self.deployments)
        raise GateError(f"unexpected collection: {endpoint}")


class EvidenceFixture(unittest.TestCase):
    def setUp(self):
        self.config = configured_policy()
        self.api = FixtureAPI(self.config)

    def evaluate(self, lifecycle="merge", identity="pr:1"):
        collector = Collector(REPOSITORY, self.api, NOW)
        if lifecycle == "archive":
            identity = "change:local:demo"
            collector.archive_context = COLLECTOR.validate_archive_context(
                lifecycle, REVISION, REVISION, "demo", identity, "local", "1", "1", REPOSITORY)
            for check in self.api.checks:
                summary = json.loads(check["output"]["summary"] or "{}")
                summary["identity"] = identity
                check["output"]["summary"] = json.dumps(summary)
        return evaluate(self.config, collector,
                        lifecycle, REVISION, identity, BASE_REVISION)


class ManifestTests(EvidenceFixture):
    def test_valid_manifest_for_all_lifecycles(self):
        for lifecycle in ("merge", "release", "archive"):
            with self.subTest(lifecycle=lifecycle):
                manifest = self.evaluate(lifecycle)
                validate_manifest(manifest, self.config, lifecycle, REVISION,
                                  manifest["identity"], NOW)
                self.assertEqual({entry["gate"] for entry in manifest["gates"]},
                                 required_gates(lifecycle))

    def test_unconfigured_policy_fails_closed(self):
        with self.assertRaisesRegex(GateError, "configure"):
            validate_config(load_json(POLICY_PATH.read_text(encoding="utf-8")))

    def test_unknown_missing_duplicate_and_malformed_manifest(self):
        original = self.evaluate()
        mutations = (
            lambda manifest: manifest.update(schema_version=2),
            lambda manifest: manifest.pop("generated_at"),
            lambda manifest: manifest["gates"].append(manifest["gates"][0]),
            lambda manifest: manifest["gates"].pop(),
            lambda manifest: manifest.update(gates="passed"),
            lambda manifest: manifest.update(revision=OTHER_REVISION),
            lambda manifest: manifest.update(repository="attacker/repo"),
            lambda manifest: manifest.update(config_sha256="0" * 64),
            lambda manifest: manifest.update(generated_at="2020-01-01T00:00:00Z"),
        )
        for mutate in mutations:
            manifest = copy.deepcopy(original)
            mutate(manifest)
            with self.subTest(manifest=manifest), self.assertRaises(GateError):
                validate_manifest(manifest, self.config, "merge", REVISION, "pr:1", NOW)

    def test_untrusted_entry_and_malformed_timestamp_rejected(self):
        original = self.evaluate()
        mutations = (
            {"source": {"kind": "check", "app_id": 1, "name": "Author claims"}},
            {"status": "failed"}, {"applicable": "false"}, {"observed_at": "yesterday"},
            {"reference": f"https://api.github.com/repos/{REPOSITORY}/../attacker"},
            {"scope": {"required": False}}, {"revision": OTHER_REVISION},
        )
        for fields in mutations:
            manifest = copy.deepcopy(original)
            manifest["gates"][0].update(fields)
            with self.subTest(fields=fields), self.assertRaises(GateError):
                validate_manifest(manifest, self.config, "merge", REVISION, "pr:1", NOW)

    def test_configuration_cannot_remove_gate_or_wait_on_self(self):
        mutations = (
            lambda config: config["lifecycles"]["merge"].pop("security"),
            lambda config: config["lifecycles"]["merge"]["security"]["source"].update(
                name="Fabric / merge"),
            lambda config: config.update(manifest_max_age_seconds=0),
            lambda config: config.update(schema_version=True),
        )
        for mutate in mutations:
            config = copy.deepcopy(self.config)
            mutate(config)
            with self.assertRaises(GateError):
                validate_config(config)

    def test_reused_source_cannot_supply_two_gates(self):
        gates = self.config["lifecycles"]["merge"]
        gates["security"]["source"] = copy.deepcopy(gates["ci"]["source"])
        with self.assertRaisesRegex(GateError, "reused"):
            validate_config(self.config)

    def test_strict_json_duplicate_keys_and_nonfinite_values(self):
        for text in ('{"gate":1,"gate":2}', '{"value":NaN}', "{broken}"):
            with self.subTest(text=text), self.assertRaises(GateError):
                load_json(text)

    def test_freshness_is_bounded_and_future_dates_rejected(self):
        fresh(OBSERVED, NOW, 301)
        for observed in ("2026-11-07T12:06:01Z", "2026-11-07T11:00:00Z", "2026-11-07Z"):
            with self.subTest(observed=observed), self.assertRaises(GateError):
                fresh(observed, NOW, 301)

    def test_schema_fields_match_generated_manifest(self):
        schema = load_json((RUNTIME / "gate-evidence.schema.json").read_text())
        manifest = self.evaluate()
        self.assertEqual(set(schema["required"]), set(manifest))
        self.assertEqual(set(schema["$defs"]["gate"]["required"]), set(manifest["gates"][0]))
        self.assertEqual(set(schema["$defs"]["gate"]["properties"]["gate"]["enum"]),
                         required_gates("archive"))


class CheckEvidenceTests(EvidenceFixture):
    def test_failed_missing_skipped_waiting_stale_and_superseded_checks(self):
        original = copy.deepcopy(self.api.checks)
        changes = (
            lambda checks: checks.pop(),
            lambda checks: checks[0].update(conclusion="failure"),
            lambda checks: checks[0].update(conclusion="neutral"),
            lambda checks: checks[0].update(status="in_progress"),
            lambda checks: checks[0].update(head_sha=OTHER_REVISION),
            lambda checks: checks[0].update(completed_at="2020-01-01T00:00:00Z"),
            lambda checks: checks.append(dict(checks[0], id=999)),
            lambda checks: checks[0]["app"].update(id=1),
            lambda checks: checks[0]["app"].update(slug="github-actions"),
        )
        for mutate in changes:
            self.api.checks = copy.deepcopy(original)
            mutate(self.api.checks)
            with self.subTest(mutate=mutate), self.assertRaises(GateError):
                self.evaluate()

    def test_generic_approval_cannot_replace_acceptance_check(self):
        self.api.checks = [check for check in self.api.checks
                           if check["name"] != "Fabric evidence / acceptance"]
        self.api.reviews = [{"id": 100, "user": {"id": 10}, "state": "APPROVED",
                             "commit_id": REVISION, "submitted_at": OBSERVED, "body": "LGTM"}]
        with self.assertRaisesRegex(GateError, "acceptance"):
            self.evaluate()

    def test_current_head_and_base_binding(self):
        for field, value in (("head", {"sha": OTHER_REVISION}),
                             ("state", "closed"), ("base", {"ref": "untrusted"})):
            original = copy.deepcopy(self.api.pull)
            self.api.pull[field] = value
            with self.subTest(field=field), self.assertRaises(GateError):
                self.evaluate()
            self.api.pull = original

    def test_head_change_during_evaluation_fails(self):
        collector = Collector(REPOSITORY, self.api, NOW)
        original = collector.evidence

        def change_head(*arguments):
            result = original(*arguments)
            self.api.pull["head"]["sha"] = OTHER_REVISION
            return result

        with (patch.object(collector, "evidence", side_effect=change_head),
              self.assertRaisesRegex(GateError, "head changed")):
            evaluate(self.config, collector, "merge", REVISION, "pr:1", BASE_REVISION)

    def test_unavailable_source_does_not_produce_manifest(self):
        with (patch.object(self.api, "pages", side_effect=GateError("source unavailable")),
              self.assertRaisesRegex(GateError, "unavailable")):
            self.evaluate()


class ScopeTests(EvidenceFixture):
    def set_scope(self, gate="coverage", lifecycle="merge", required=False):
        rule = self.config["lifecycles"][lifecycle][gate]
        rule["scope"] = {"source": {"kind": "check", "app_id": APP_ID,
                                   "name": f"Fabric scope / {gate}"},
                         "allowed_rules": {"no-new-code": "No added executable code"}}
        disposition = {"gate": gate, "revision": REVISION, "lifecycle": lifecycle,
                       "required": required, "scope_rule": None if required else "no-new-code",
                       "reason": None if required else "No added executable code"}
        check = check_record(901, rule["scope"]["source"]["name"])
        check["output"]["summary"] = json.dumps(disposition)
        self.api.checks.append(check)
        return disposition, check

    def test_trusted_scope_reason_and_source_pass(self):
        self.set_scope()
        manifest = self.evaluate()
        coverage = next(entry for entry in manifest["gates"] if entry["gate"] == "coverage")
        self.assertEqual(coverage["status"], "not_applicable")
        self.assertEqual(coverage["source"]["name"], "Fabric scope / coverage")

    def test_required_scope_still_requires_gate(self):
        self.set_scope(required=True)
        self.api.checks = [check for check in self.api.checks
                           if check["name"] != "Fabric evidence / coverage"]
        with self.assertRaisesRegex(GateError, "coverage"):
            self.evaluate()

    def test_missing_ambiguous_stale_or_untrusted_scope_fails(self):
        disposition, check = self.set_scope()
        for fields in ({"required": "false"}, {"reason": ""}, {"scope_rule": "author-waiver"},
                       {"revision": OTHER_REVISION}, {"lifecycle": "archive"}):
            changed = dict(disposition, **fields)
            check["output"]["summary"] = json.dumps(changed)
            with self.subTest(fields=fields), self.assertRaises(GateError):
                self.evaluate()
        self.api.checks.remove(check)
        with self.assertRaisesRegex(GateError, "scope"):
            self.evaluate()

    def test_mandatory_planning_cannot_be_waived(self):
        self.set_scope("planning")
        with self.assertRaisesRegex(GateError, "cannot be waived"):
            self.evaluate()

    def test_no_deployment_scope_does_not_imply_no_operational_gates(self):
        self.set_scope("deployment", "archive")
        self.api.checks = [check for check in self.api.checks
                           if check["name"] != "Fabric evidence / stability"]
        with self.assertRaisesRegex(GateError, "stability"):
            self.evaluate("archive")


class ReviewTests(EvidenceFixture):
    def set_review(self, gate="acceptance", body="fabric-gate:acceptance:approved"):
        self.config["lifecycles"]["merge"][gate]["source"] = {
            "kind": "review", "reviewer_ids": [10], "marker": f"fabric-gate:{gate}:approved"}
        self.api.reviews = [{"id": 100, "user": {"id": 10}, "state": "APPROVED",
                             "commit_id": REVISION, "submitted_at": OBSERVED, "body": body}]

    def test_explicit_gate_review_passes(self):
        self.set_review()
        manifest = self.evaluate()
        acceptance = next(entry for entry in manifest["gates"] if entry["gate"] == "acceptance")
        self.assertIn("/pulls/1/reviews/100", acceptance["reference"])
        self.assertNotIn("body", json.dumps(manifest))

    def test_generic_review_not_proposal_security_or_legal_evidence(self):
        for gate in ("acceptance", "security", "legal"):
            self.set_review(gate, "LGTM")
            with self.subTest(gate=gate), self.assertRaises(GateError):
                self.evaluate()
            self.config = configured_policy()

    def test_wrong_reviewer_revision_and_superseded_review_fail(self):
        for fields in ({"user": {"id": 99}}, {"commit_id": OTHER_REVISION},
                       {"submitted_at": "2020-01-01T00:00:00Z"}, {"state": "DISMISSED"}):
            self.set_review()
            self.api.reviews[0].update(fields)
            with self.subTest(fields=fields), self.assertRaises(GateError):
                self.evaluate()
        self.set_review()
        self.api.reviews.append(dict(self.api.reviews[0], id=101, state="CHANGES_REQUESTED"))
        with self.assertRaisesRegex(GateError, "superseded"):
            self.evaluate()

    def test_generic_approval_only_allowed_for_code_review(self):
        self.set_review("code_review", "LGTM")
        self.config["lifecycles"]["merge"]["code_review"]["source"]["marker"] = ""
        self.evaluate()
        self.config["lifecycles"]["merge"]["security"]["source"] = {
            "kind": "review", "reviewer_ids": [10], "marker": ""}
        with self.assertRaisesRegex(GateError, "marker"):
            self.evaluate()


class LifecycleTests(EvidenceFixture):
    def test_missing_or_failing_release_evidence_blocks(self):
        release_check = next(check for check in self.api.checks
                             if check["name"] == "Fabric evidence / release_readiness")
        for conclusion in ("failure", "skipped"):
            release_check["conclusion"] = conclusion
            with self.assertRaisesRegex(GateError, "release_readiness"):
                self.evaluate("release")
        self.api.checks.remove(release_check)
        with self.assertRaisesRegex(GateError, "release_readiness"):
            self.evaluate("release")

    def test_operations_are_archive_only(self):
        self.api.statuses = []
        self.evaluate("merge")
        self.evaluate("release")
        with self.assertRaisesRegex(GateError, "deployment"):
            self.evaluate("archive")

    def test_deployed_revision_environment_creator_and_latest_status(self):
        original = copy.deepcopy(self.api.deployments)
        for fields in ({"sha": OTHER_REVISION}, {"environment": "staging"},
                       {"creator": {"id": 99}}):
            self.api.deployments = [dict(original[0], **fields)]
            with self.subTest(fields=fields), self.assertRaisesRegex(GateError, "deployment"):
                self.evaluate("archive")
        self.api.deployments = original + [dict(original[0], id=82)]
        with self.assertRaisesRegex(GateError, "ambiguous"):
            self.evaluate("archive")
        self.api.deployments = original
        self.api.statuses.append(dict(self.api.statuses[0], id=90, state="inactive"))
        with self.assertRaisesRegex(GateError, "inactive"):
            self.evaluate("archive")

    def test_missing_each_operational_gate_blocks(self):
        original = copy.deepcopy(self.api.checks)
        for gate in ("slo", "alerts", "runbook", "stability", "postmortem"):
            self.api.checks = [check for check in original
                               if check["name"] != f"Fabric evidence / {gate}"]
            with self.subTest(gate=gate), self.assertRaisesRegex(GateError, gate):
                self.evaluate("archive")

    def test_parent_preflight_stops_before_any_spec_writes_or_moves(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        policy = root / ".github/skills/fabric-verify-change/scripts/gate-policy.json"
        policy.parent.mkdir(parents=True)
        policy.write_text(json.dumps(self.config), encoding="utf-8")
        self.api.statuses = []
        for check in self.api.checks:
            check["output"]["summary"] = json.dumps({"identity": "change:local:demo"})
        write_specs = Mock()
        move_change = Mock()
        with (patch("collect_fabric_evidence.trusted_checkout", return_value=BASE_REVISION),
              self.assertRaisesRegex(GateError, "deployment")):
            preflight(root, REPOSITORY, "archive", REVISION, "change:local:demo", self.api, NOW,
                      deployed_revision=REVISION, change="demo", store="local",
                      pr_number="1", release_id="1", deployed_repository=REPOSITORY)
            write_specs()
            move_change()
        write_specs.assert_not_called()
        move_change.assert_not_called()

    def test_missing_explicit_deployed_repository_blocks_before_api_reads(self):
        with self.assertRaisesRegex(GateError, "deployed repository"):
            preflight(ROOT, REPOSITORY, "archive", REVISION, "change:local:demo", self.api, NOW,
                      deployed_revision=OTHER_REVISION, change="demo")
        self.assertFalse(self.api.calls)

    def test_archive_release_pr_relation_is_verified(self):
        for fields in ({"merged": False}, {"merge_commit_sha": OTHER_REVISION}):
            original = copy.deepcopy(self.api.pull)
            self.api.pull.update(fields)
            with self.subTest(fields=fields), self.assertRaisesRegex(GateError, "merged revision"):
                self.evaluate("archive")
            self.api.pull = original

    def test_selected_store_identity_is_not_interchangeable(self):
        collector = Collector(REPOSITORY, self.api, NOW)
        identity = "change:store:shared:demo"
        collector.archive_context = COLLECTOR.validate_archive_context(
            "archive", REVISION, REVISION, "demo", identity, "store:shared", "1", "1", REPOSITORY)
        for check in self.api.checks:
            check["output"]["summary"] = json.dumps({"identity": "change:local:demo"})
        with self.assertRaisesRegex(GateError, "store/change identity"):
            evaluate(self.config, collector, "archive", REVISION, identity, BASE_REVISION)
        for check in self.api.checks:
            check["output"]["summary"] = json.dumps({"identity": identity})
        successful = Collector(REPOSITORY, self.api, NOW)
        successful.archive_context = copy.deepcopy(collector.archive_context)
        manifest = evaluate(self.config, successful,
                            "archive", REVISION, identity, BASE_REVISION)
        self.assertEqual(manifest["archive_context"]["store"], "store:shared")

    def test_published_release_and_actual_tag_revision_required_at_archive(self):
        original = self.api.get
        for draft, resolved in ((True, REVISION), (False, OTHER_REVISION)):
            def override(endpoint, draft=draft, resolved=resolved):
                if endpoint.endswith("/releases/1"):
                    return {"id": 1, "draft": draft, "published_at": OBSERVED, "tag_name": "v1"}
                if endpoint.endswith("/git/ref/tags/v1"):
                    return {"object": {"type": "commit", "sha": resolved}}
                return original(endpoint)
            with (patch.object(self.api, "get", side_effect=override),
                  self.assertRaises(GateError)):
                self.evaluate("archive")


class APIBoundaryTests(unittest.TestCase):
    def test_unprotected_default_branch_is_not_trusted(self):
        api = Mock()
        api.get.side_effect = [{"default_branch": "main"},
                               {"protected": False, "commit": {"sha": BASE_REVISION}}]
        with self.assertRaisesRegex(GateError, "protection"):
            trusted_checkout(ROOT, REPOSITORY, api)

    def test_cli_does_not_accept_supplied_manifest(self):
        result = subprocess.run(
            [sys.executable, str(RUNTIME / "collect_fabric_evidence.py"),
             "--lifecycle", "merge", "--revision", REVISION, "--manifest", "author.json"],
            capture_output=True, text=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unrecognized arguments", result.stderr)

    def test_timeout_unavailable_and_invalid_json_fail(self):
        errors = (OSError("unavailable"), subprocess.TimeoutExpired("gh", 20))
        for error in errors:
            with (patch("collect_fabric_evidence.subprocess.run", side_effect=error),
                  self.assertRaisesRegex(GateError, "unavailable")):
                GitHubAPI().get("repos/owner/repo")
        for code, content in ((1, b"denied"), (0, b"{bad"), (0, b"\xff")):
            with (patch("collect_fabric_evidence.subprocess.run",
                        return_value=Mock(returncode=code, stdout=content)),
                  self.assertRaises(GateError)):
                GitHubAPI().get("repos/owner/repo")

    def test_request_deadline_response_and_pagination_bounds(self):
        api = GitHubAPI()
        api.requests = 80
        with self.assertRaisesRegex(GateError, "budget"):
            api.get("repos/owner/repo")
        api = GitHubAPI()
        api.deadline = 0
        with self.assertRaisesRegex(GateError, "deadline"):
            api.get("repos/owner/repo")
        with (patch.object(GitHubAPI, "get", return_value=[{"id": index} for index in range(100)]),
              self.assertRaisesRegex(GateError, "pagination")):
            GitHubAPI().pages("repos/owner/repo/pulls")
        with (patch("collect_fabric_evidence.subprocess.run",
                    return_value=Mock(returncode=0, stdout=b" " * (4 * 1024 * 1024 + 1))),
              self.assertRaisesRegex(GateError, "bound")):
            GitHubAPI().get("repos/owner/repo")

    def test_duplicate_and_malformed_api_records_fail(self):
        for records in ([{"id": 1}, {"id": 1}], [{"id": True}], ["not an object"]):
            with (patch.object(GitHubAPI, "get", return_value=records),
                  self.assertRaises(GateError)):
                GitHubAPI().pages("repos/owner/repo/pulls")

    def test_trusted_checkout_rejects_head_and_owned_file_modification(self):
        api = FixtureAPI(configured_policy())
        clean = Mock(returncode=0, stdout="")
        with (patch("collect_fabric_evidence.subprocess.run",
                    side_effect=[Mock(returncode=0, stdout=OTHER_REVISION), clean]),
              self.assertRaisesRegex(GateError, "trusted base")):
            trusted_checkout(ROOT, REPOSITORY, api)
        with (patch("collect_fabric_evidence.subprocess.run",
                    side_effect=[Mock(returncode=0, stdout=BASE_REVISION),
                                 Mock(returncode=0, stdout=" M owned-runtime.py")]),
              self.assertRaisesRegex(GateError, "modified")):
            trusted_checkout(ROOT, REPOSITORY, api)


class ControlTests(unittest.TestCase):
    def test_merge_publishes_on_current_head_and_fails_closed(self):
        api = FixtureAPI(configured_policy())
        with (patch("run_fabric_gate_control.protected_policy", return_value=configured_policy()),
              patch("run_fabric_gate_control.start_check", return_value=1),
              patch("run_fabric_gate_control.finish_check") as status,
              patch("run_fabric_gate_control.preflight", side_effect=GateError("security")),
              self.assertRaises(GateError)):
            merge_control(ROOT, REPOSITORY, "1", api)
        self.assertEqual(status.call_args.args[-1], "failure")
        self.assertEqual(status.call_args.args[3], REVISION)

    def test_release_failure_never_publishes_draft(self):
        draft = {"id": 1, "draft": True, "tag_name": "v1"}
        api = Mock()
        with (patch("run_fabric_gate_control.release_snapshot", return_value=(draft, REVISION)),
              patch("run_fabric_gate_control.preflight", side_effect=GateError("legal")),
              patch("run_fabric_gate_control.protected_policy", return_value=configured_policy()),
              patch("run_fabric_gate_control.start_check", return_value=1),
              patch("run_fabric_gate_control.finish_check"),
              self.assertRaises(GateError)):
            release_control(ROOT, REPOSITORY, "1", api)
        api.mutate.assert_not_called()

    def test_release_changed_draft_or_tag_never_publishes(self):
        draft = {"id": 1, "draft": True, "tag_name": "v1"}
        for changed in ((dict(draft, tag_name="v2"), REVISION), (draft, OTHER_REVISION)):
            api = Mock()
            with (patch("run_fabric_gate_control.release_snapshot",
                        side_effect=[(draft, REVISION), changed]),
                  patch("run_fabric_gate_control.preflight", return_value={}),
                  patch("run_fabric_gate_control.protected_policy", return_value=configured_policy()),
                  patch("run_fabric_gate_control.start_check", return_value=1),
                  patch("run_fabric_gate_control.finish_check"),
                  self.assertRaisesRegex(GateError, "changed")):
                release_control(ROOT, REPOSITORY, "1", api)
            api.mutate.assert_not_called()

    def test_successful_release_publishes_only_after_gate_and_recheck(self):
        draft = {"id": 1, "draft": True, "tag_name": "v1"}
        api = Mock()
        with (patch("run_fabric_gate_control.release_snapshot", return_value=(draft, REVISION)),
              patch("run_fabric_gate_control.preflight", return_value={}),
              patch("run_fabric_gate_control.protected_policy", return_value=configured_policy()),
              patch("run_fabric_gate_control.start_check", return_value=1),
              patch("run_fabric_gate_control.validate_manifest"),
              patch("run_fabric_gate_control.finish_check") as status):
            release_control(ROOT, REPOSITORY, "1", api)
        api.mutate.assert_called_once_with(f"repos/{REPOSITORY}/releases/1", {"draft": False}, "PATCH")
        self.assertEqual(status.call_args.args[-1], "success")

    def test_release_revision_resolves_annotated_tag_and_rejects_missing_draft(self):
        api = Mock()
        api.get.side_effect = [
            {"id": 1, "draft": True, "tag_name": "v1"},
            {"object": {"type": "tag", "sha": BASE_REVISION}},
            {"object": {"type": "commit", "sha": REVISION}},
        ]
        self.assertEqual(release_snapshot(api, REPOSITORY, 1)[1], REVISION)
        api.get.side_effect = [{"id": 1, "draft": False, "tag_name": "v1"}]
        with self.assertRaisesRegex(GateError, "draft"):
            release_snapshot(api, REPOSITORY, 1)


if __name__ == "__main__":
    unittest.main()
