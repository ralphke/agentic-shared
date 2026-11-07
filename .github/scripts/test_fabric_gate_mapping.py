"""Accepted trusted-mapping scenarios; all links are independent API fixtures."""

import copy
import importlib
import json
import unittest
from unittest.mock import patch

from test_fabric_gate import (
    APP_ID,
    BASE_REVISION,
    COLLECTOR,
    EVALUATOR,
    NOW,
    OBSERVED,
    OTHER_REVISION,
    REPOSITORY,
    REVISION,
    Collector,
    FixtureAPI,
    GateError,
    check_record,
    configured_policy,
)

MAPPING = importlib.import_module("fabric_mapping")
IDENTITY = "change:store:product-planning:demo"


class MappingAPI(FixtureAPI):
    def __init__(self, config, deployed_repository=REPOSITORY):
        super().__init__(config)
        self.deployed_repository = deployed_repository
        self.deployments[0]["sha"] = OTHER_REVISION
        self.checks = [dict(check, output={"summary": json.dumps({"identity": IDENTITY})})
                       for check in self.checks]
        operational = [dict(check, id=check["id"] + 200, head_sha=OTHER_REVISION)
                       for check in self.checks if check["name"].split(" / ")[1]
                       in EVALUATOR.ARCHIVE_GATES]
        self.checks.extend(operational)
        self.tag_sha = OTHER_REVISION

    def get(self, endpoint):
        if endpoint.endswith("/releases/1"):
            return {"id": 1, "draft": False, "published_at": OBSERVED, "tag_name": "v1"}
        if endpoint.endswith("/git/ref/tags/v1"):
            return {"object": {"type": "commit", "sha": self.tag_sha}}
        if endpoint.endswith("/deployments/80"):
            return copy.deepcopy(self.deployments[0])
        return super().get(endpoint)

    def pages(self, endpoint, field=None):
        if "check-runs" in endpoint:
            evaluated = f"commits/{REVISION}/" in endpoint
            return copy.deepcopy([check for check in self.checks
                                  if (check["head_sha"] == REVISION) == evaluated])
        return super().pages(endpoint, field)


class MappingTests(unittest.TestCase):
    def setUp(self):
        self.config = configured_policy()
        self.config["mapping"] = {"source": {"kind": "check", "app_id": APP_ID + 2,
            "name": "Fabric mapping / change_deployment_mapping"}, "max_age_seconds": 900,
            "repository_pairs": [{"evaluated": REPOSITORY, "deployed": REPOSITORY}]}
        self.api = MappingAPI(self.config)
        self.record = {"schema_version": 1, "gate": "change_deployment_mapping",
            "identity": IDENTITY, "evaluated_repository": REPOSITORY,
            "evaluated_revision": REVISION, "deployed_repository": REPOSITORY,
            "deployed_revision": OTHER_REVISION,
            "pull_request": {"repository": REPOSITORY, "number": 1, "evaluated_revision": REVISION},
            "release": {"repository": REPOSITORY, "id": 1,
                        "tag_object_sha": OTHER_REVISION, "commit_sha": OTHER_REVISION},
            "deployment": {"repository": REPOSITORY, "id": 80, "status_id": 81,
                           "environment": "production", "revision": OTHER_REVISION},
            "observed_at": OBSERVED, "expires_at": "2026-11-07T12:10:00Z"}
        self.check = check_record(900, self.config["mapping"]["source"]["name"])
        self.check["app"]["id"] = APP_ID + 2
        self.api.checks.append(self.check)

    def evaluate(self, deployed_repository=REPOSITORY):
        self.check["output"]["summary"] = json.dumps(self.record)
        collector = Collector(REPOSITORY, self.api, NOW)
        collector.archive_context = COLLECTOR.validate_archive_context(
            "archive", REVISION, OTHER_REVISION, "demo", IDENTITY,
            "store:product-planning", "1", "1", deployed_repository)
        return EVALUATOR.evaluate(self.config, collector, "archive", REVISION, IDENTITY, BASE_REVISION)

    def test_valid_mapping_binds_change_and_operational_revisions(self):
        self.api.pull.update(state="closed", merged=True, merge_commit_sha=BASE_REVISION)
        manifest = self.evaluate()
        for entry in manifest["gates"]:
            expected = OTHER_REVISION if entry["gate"] in EVALUATOR.ARCHIVE_GATES else REVISION
            self.assertEqual(entry["revision"], expected)
        self.assertEqual(manifest["archive_context"]["mapping"]["source"]["app_id"], APP_ID + 2)
        self.assertIn("/check-runs/900", manifest["archive_context"]["mapping"]["reference"])

    def test_unmerged_mapped_pr_blocks_initial_archive_preflight(self):
        self.api.pull["merged"] = False
        with self.assertRaisesRegex(GateError, "mapping PR must be merged"):
            self.evaluate()
        self.assertEqual(self.api.calls.count(f"repos/{REPOSITORY}/pulls/1"), 1)

    def test_controlled_premerge_still_accepts_an_open_unmerged_pr(self):
        self.api.pull.update(state="open", merged=False)
        manifest = EVALUATOR.evaluate(self.config, Collector(REPOSITORY, self.api, NOW),
                                      "merge", REVISION, "pr:1", BASE_REVISION)
        self.assertEqual(manifest["lifecycle"], "merge")
        self.assertIsNone(manifest["archive_context"])

    def test_unmerged_mapped_pr_blocks_final_archive_recheck(self):
        original = self.api.get
        queries = []

        def unmerged_at_recheck(endpoint):
            if endpoint == f"repos/{REPOSITORY}/pulls/1":
                queries.append(endpoint)
                if len(queries) > 1:
                    self.api.pull["merged"] = False
            return original(endpoint)

        with (patch.object(self.api, "get", side_effect=unmerged_at_recheck),
              self.assertRaisesRegex(GateError, "mapping PR must be merged")):
            self.evaluate()
        self.assertEqual(len(queries), 2)

    def test_missing_duplicate_untrusted_and_actions_mapping_fail(self):
        self.api.checks.remove(self.check)
        with self.assertRaisesRegex(GateError, "missing"):
            self.evaluate()
        self.api.checks.extend([self.check, dict(self.check, id=901)])
        with self.assertRaisesRegex(GateError, "ambiguous"):
            self.evaluate()
        self.api.checks.pop()
        self.check["app"]["slug"] = "github-actions"
        with self.assertRaisesRegex(GateError, "GitHub Actions"):
            self.evaluate()
        self.check["app"]["id"] = 1
        with self.assertRaisesRegex(GateError, "missing"):
            self.evaluate()

    def test_identity_revision_schema_expiry_and_missing_links_fail(self):
        original = copy.deepcopy(self.record)
        for fields in ({"identity": "change:local:demo"}, {"evaluated_revision": BASE_REVISION},
                       {"deployed_revision": REVISION}, {"schema_version": 99},
                       {"expires_at": OBSERVED}, {"observed_at": "2020-01-01T00:00:00Z"},
                       {"release": {}}, {"deployment": {}}, {"pull_request": {}}):
            self.record = dict(original, **fields)
            with self.subTest(fields=fields), self.assertRaises(GateError):
                self.evaluate()

    def test_latest_status_failure_or_supersession_and_wrong_release_fail(self):
        self.api.statuses.append(dict(self.api.statuses[0], id=90))
        with self.assertRaisesRegex(GateError, "superseded"):
            self.evaluate()
        self.api.statuses.pop()
        self.api.statuses[0]["state"] = "failure"
        with self.assertRaisesRegex(GateError, "unsuccessful"):
            self.evaluate()
        self.api.statuses[0]["state"] = "success"
        self.api.tag_sha = BASE_REVISION
        with self.assertRaisesRegex(GateError, "release/tag"):
            self.evaluate()

    def test_release_tag_is_independently_rechecked(self):
        original = self.api.get
        queries = []

        def changed_tag(endpoint):
            if endpoint.endswith("/git/ref/tags/v1"):
                queries.append(endpoint)
                if len(queries) > 1:
                    self.api.tag_sha = BASE_REVISION
            return original(endpoint)

        with (patch.object(self.api, "get", side_effect=changed_tag),
              self.assertRaisesRegex(GateError, "release/tag")):
            self.evaluate()
        self.assertEqual(len(queries), 2)

    def test_configuration_absence_and_ancestry_do_not_authorize_mapping(self):
        self.config["mapping"] = None
        with self.assertRaisesRegex(GateError, "configured trusted mapping"):
            self.evaluate()
        self.assertFalse(any("compare/" in endpoint for endpoint in self.api.calls))

    def test_explicit_cross_repository_pair_not_inferred_from_store(self):
        deployed = "owner/deployment"
        with self.assertRaises(GateError):
            self.evaluate(deployed)
        self.config["mapping"]["repository_pairs"] = [{"evaluated": REPOSITORY, "deployed": deployed}]
        self.record["deployed_repository"] = deployed
        self.record["release"]["repository"] = deployed
        self.record["deployment"]["repository"] = deployed
        manifest = self.evaluate(deployed)
        self.assertEqual(manifest["archive_context"]["deployed_repository"], deployed)
        deployment = next(entry for entry in manifest["gates"] if entry["gate"] == "deployment")
        self.assertIn("repos/owner/deployment/", deployment["reference"])

    def test_unavailable_link_and_missing_operational_gate_prevent_success(self):
        with (patch.object(self.api, "get", side_effect=GateError("unavailable")),
              self.assertRaises(GateError)):
            self.evaluate()
        self.api.checks = [check for check in self.api.checks
                           if check["name"] != "Fabric evidence / stability"]
        with self.assertRaisesRegex(GateError, "stability"):
            self.evaluate()


if __name__ == "__main__":
    unittest.main()
