"""Exclusive App provenance, admin prerequisites and explicit merge boundary tests."""

import copy
import importlib
import unittest
from unittest.mock import Mock, patch

from test_fabric_gate import (
    APP_ID,
    CONTROL,
    REPOSITORY,
    REVISION,
    ROOT,
    FixtureAPI,
    GateError,
    configured_policy,
)

POLICY = importlib.import_module("fabric_control_policy")


def protected_branch():
    return {"enforce_admins": {"enabled": True},
            "restrictions": {"users": [], "teams": [], "apps": [{"id": APP_ID}]},
            "required_status_checks": {"strict": True, "checks": [
                {"context": "Fabric / merge", "app_id": APP_ID}]},
            "required_pull_request_reviews": {"dismiss_stale_reviews": True,
                "required_approving_review_count": 1, "require_code_owner_reviews": True,
                "bypass_pull_request_allowances": {"users": [], "teams": [], "apps": []}},
            "allow_force_pushes": {"enabled": False}, "allow_deletions": {"enabled": False}}


class SetupAPI:
    def __init__(self):
        self.protection = protected_branch()
        self.environment = {"deployment_branch_policy": {
            "protected_branches": False, "custom_branch_policies": True},
            "protection_rules": [{"type": "required_reviewers", "prevent_self_review": True,
                                 "reviewers": [{"type": "User", "reviewer": {"id": 10}}]}]}
        self.branch_policies = [{"id": 1, "name": "main", "type": "branch"}]
        self.repo_secrets = []
        self.org_secrets = []
        self.rulesets = []

    def get(self, endpoint):
        if endpoint.startswith("installation/repositories"):
            return {"total_count": 1, "repositories": [{"full_name": REPOSITORY}]}
        if endpoint.endswith("/protection"):
            return self.protection
        if "/environments/" in endpoint:
            return self.environment
        return {"default_branch": "main", "allow_auto_merge": False, "allow_squash_merge": True}

    def pages(self, endpoint, field=None, identity_key="id"):
        if endpoint.endswith("/deployment-branch-policies"):
            return self.branch_policies
        if endpoint.endswith("/actions/organization-secrets"):
            return self.org_secrets
        if endpoint.endswith("/actions/secrets"):
            return self.repo_secrets
        if endpoint.endswith("/secrets"):
            return [{"name": "FABRIC_GATE_APP_TOKEN"}]
        return self.rulesets


class PrerequisiteTests(unittest.TestCase):
    def setUp(self):
        self.api = SetupAPI()
        self.policy = configured_policy()["control"]

    def test_exact_exclusive_setup_passes_without_configuring_anything(self):
        self.assertEqual(POLICY.validate_setup(self.api, REPOSITORY, self.policy), "main")

    def test_shared_app_status_source_bypass_and_broad_writers_fail(self):
        original = copy.deepcopy(self.api.protection)
        mutations = (
            lambda value: value["restrictions"].update(users=[{"id": 99}]),
            lambda value: value["restrictions"].update(apps=[{"id": 15368}]),
            lambda value: value["required_status_checks"]["checks"][0].update(app_id=15368),
            lambda value: value["enforce_admins"].update(enabled=False),
            lambda value: value["required_status_checks"].update(strict=False),
            lambda value: value["allow_force_pushes"].update(enabled=True),
            lambda value: value.pop("allow_deletions"),
        )
        for mutate in mutations:
            self.api.protection = copy.deepcopy(original)
            mutate(self.api.protection)
            with self.assertRaises(GateError):
                POLICY.validate_setup(self.api, REPOSITORY, self.policy)

    def test_pr_ref_wildcard_repo_secret_org_secret_and_unavailable_setup_fail(self):
        self.api.branch_policies[0]["name"] = "*"
        with self.assertRaises(GateError):
            POLICY.validate_setup(self.api, REPOSITORY, self.policy)
        self.api.branch_policies[0]["name"] = "main"
        for target in ("repo_secrets", "org_secrets"):
            setattr(self.api, target, [{"name": "FABRIC_GATE_APP_TOKEN"}])
            with self.assertRaises(GateError):
                POLICY.validate_setup(self.api, REPOSITORY, self.policy)
            setattr(self.api, target, [])
        with (patch.object(self.api, "get", side_effect=GateError("unavailable")),
              self.assertRaises(GateError)):
            POLICY.validate_setup(self.api, REPOSITORY, self.policy)

    def test_missing_reviewers_or_active_rulesets_do_not_become_exemptions(self):
        self.api.environment["protection_rules"] = []
        with self.assertRaises(GateError):
            POLICY.validate_setup(self.api, REPOSITORY, self.policy)
        self.api.rulesets = [{"id": 1, "enforcement": "active"}]
        with self.assertRaises(GateError):
            POLICY.validate_setup(self.api, REPOSITORY, self.policy)

    def test_independent_custody_assertion_is_required(self):
        collector = Mock(repository=REPOSITORY)
        collector.check.return_value = {"output": {"summary": "{}"}}
        with self.assertRaisesRegex(GateError, "custody"):
            POLICY.verify_custody(collector, REVISION, self.policy)

    def test_native_auto_merge_cannot_be_an_alternate_path(self):
        original = self.api.get

        def enabled_auto_merge(endpoint):
            response = original(endpoint)
            if endpoint == f"repos/{REPOSITORY}":
                response = dict(response, allow_auto_merge=True)
            return response

        with (patch.object(self.api, "get", side_effect=enabled_auto_merge),
              self.assertRaisesRegex(GateError, "auto-merge")):
            POLICY.validate_setup(self.api, REPOSITORY, self.policy)


class AppProvenanceTests(unittest.TestCase):
    def test_shared_github_token_cannot_publish_required_gate_app_verdict(self):
        api = Mock()
        api.mutate.return_value = {"id": 1, "name": "Fabric / merge", "head_sha": REVISION,
                                  "app": {"id": 15368, "slug": "github-actions"}}
        with self.assertRaisesRegex(GateError, "unique gate-only App"):
            CONTROL.start_check(api, REPOSITORY, REVISION, "Fabric / merge",
                                configured_policy()["control"])
        self.assertEqual(api.mutate.call_count, 1)
        self.assertEqual(api.mutate.call_args.args[1]["status"], "in_progress")
        self.assertNotIn("conclusion", api.mutate.call_args.args[1])

    def test_verdict_updates_authenticate_app_head_name_and_check_id(self):
        api = Mock()
        original = {"id": 1, "name": "Fabric / merge", "head_sha": REVISION,
                    "app": {"id": APP_ID, "slug": "gate-only-app"}, "conclusion": "success"}
        for fields in ({"id": 2}, {"head_sha": "c" * 40}, {"name": "Another gate"},
                       {"app": {"id": 15368, "slug": "github-actions"}}):
            api.mutate.return_value = dict(original, **fields)
            with self.assertRaises(GateError):
                CONTROL.finish_check(api, REPOSITORY, 1, REVISION, "Fabric / merge",
                                     configured_policy()["control"], "success")


class MergeBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.config = configured_policy()
        self.api = FixtureAPI(self.config)
        self.api.mutate = Mock(return_value={"merged": True})
        self.api.custody_observed_at = CONTROL.datetime.now(CONTROL.UTC).isoformat().replace("+00:00", "Z")

    def test_evaluation_never_merges_even_when_all_evidence_passes(self):
        with (patch("run_fabric_gate_control.protected_policy", return_value=self.config),
              patch("run_fabric_gate_control.preflight", return_value={}),
              patch("run_fabric_gate_control.start_check", return_value=1),
              patch("run_fabric_gate_control.finish_check")):
            CONTROL.merge_control(ROOT, REPOSITORY, "1", self.api)
        self.api.mutate.assert_not_called()

    def test_expiry_withdrawal_or_unavailable_source_blocks_explicit_merge_after_old_success(self):
        for failure in ("expired security", "withdrawn acceptance", "unavailable review"):
            with (patch("run_fabric_gate_control.protected_policy", return_value=self.config),
                  patch("run_fabric_gate_control.preflight", side_effect=[{}, GateError(failure)]),
                  patch("run_fabric_gate_control.start_check", return_value=1),
                  patch("run_fabric_gate_control.finish_check") as finish,
                  self.assertRaises(GateError)):
                CONTROL.merge_control(ROOT, REPOSITORY, "1", self.api, REVISION, True)
            self.api.mutate.assert_not_called()
            self.assertEqual(finish.call_args.args[-1], "failure")

    def test_actual_operation_rechecks_and_uses_conditional_sha(self):
        with (patch("run_fabric_gate_control.protected_policy", return_value=self.config),
              patch("run_fabric_gate_control.preflight", return_value={}) as preflight,
              patch("run_fabric_gate_control.validate_manifest"),
              patch("run_fabric_gate_control.start_check", return_value=1),
              patch("run_fabric_gate_control.finish_check")):
            CONTROL.merge_control(ROOT, REPOSITORY, "1", self.api, REVISION, True)
        self.assertEqual(preflight.call_count, 2)
        self.api.mutate.assert_called_once_with(f"repos/{REPOSITORY}/pulls/1/merge",
                                               {"sha": REVISION, "merge_method": "squash"}, "PUT")

    def test_changed_head_or_missing_confirmation_never_mutates(self):
        self.api.pull["head"]["sha"] = "c" * 40
        for expected in (None, REVISION):
            with self.assertRaises(GateError):
                CONTROL.merge_control(ROOT, REPOSITORY, "1", self.api, expected, True)
        self.api.mutate.assert_not_called()

    def test_failed_prerequisites_block_before_check_creation(self):
        with (patch("run_fabric_gate_control.protected_policy", side_effect=GateError("unsafe setup")),
              patch("run_fabric_gate_control.start_check") as start,
              self.assertRaises(GateError)):
            CONTROL.merge_control(ROOT, REPOSITORY, "1", self.api, REVISION, True)
        start.assert_not_called()
        self.api.mutate.assert_not_called()

    def test_revocation_never_merges_and_only_updates_gate_app_checks(self):
        self.api.pages = Mock(side_effect=[
            [self.api.pull],
            [{"id": 1, "name": "Fabric / merge", "app": {"id": APP_ID}},
             {"id": 2, "name": "Fabric / merge", "app": {"id": 15368}}],
        ])
        with (patch("run_fabric_gate_control.protected_policy", return_value=self.config),
              patch("run_fabric_gate_control.finish_check") as finish):
            CONTROL.invalidate(ROOT, REPOSITORY, self.api)
        finish.assert_called_once()
        self.assertEqual(finish.call_args.args[-1], "failure")
        self.api.mutate.assert_not_called()


if __name__ == "__main__":
    unittest.main()
