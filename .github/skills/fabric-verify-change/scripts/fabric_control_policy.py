"""Fail-closed prerequisites for the exclusive, environment-confined merge App."""

from urllib.parse import quote

from fabric_gate import exact_fields, load_json, require, validate_source

CONTROL_ENVIRONMENT = "fabric-gate-control"
TOKEN_SECRET = "FABRIC_GATE_APP_TOKEN"
MERGE_CHECK = "Fabric / merge"
CUSTODY_MAX_AGE_SECONDS = 900


def validate_control_policy(policy):
    """Require real administrator-supplied identities, not defaults or token claims."""
    exact_fields(policy, {"app_id", "reviewer_ids", "custody_source"}, "control policy")
    require(type(policy["app_id"]) is int and policy["app_id"] > 0,
            "configure gate-only App ID")
    validate_source(policy["custody_source"], "credential_custody")
    require(policy["custody_source"]["kind"] == "check"
            and policy["custody_source"]["app_id"] != policy["app_id"],
            "independent trusted credential-custody source required")
    reviewers = policy["reviewer_ids"]
    require(isinstance(reviewers, list) and reviewers
            and all(type(value) is int and value > 0 for value in reviewers)
            and len(reviewers) == len(set(reviewers)), "configure environment reviewers")


def validate_branch(protection, policy):
    """Classic branch protection must make the App the exclusive merge writer."""
    require(protection.get("enforce_admins", {}).get("enabled") is True,
            "administrator bypass must be disabled")
    restrictions = protection.get("restrictions") or {}
    require(restrictions.get("users") == [] and restrictions.get("teams") == []
            and [app.get("id") for app in restrictions.get("apps", [])] == [policy["app_id"]],
            "destination must restrict writers/mergers to the gate-only App")
    checks = protection.get("required_status_checks") or {}
    require(checks.get("strict") is True and any(check.get("context") == MERGE_CHECK
            and check.get("app_id") == policy["app_id"] for check in checks.get("checks", [])),
            "required Fabric / merge source must be the gate-only App")
    reviews = protection.get("required_pull_request_reviews") or {}
    require(reviews.get("dismiss_stale_reviews") is True
            and type(reviews.get("required_approving_review_count")) is int
            and reviews.get("required_approving_review_count", 0) >= 1
            and reviews.get("require_code_owner_reviews") is True,
            "current protected code review required")
    bypass = reviews.get("bypass_pull_request_allowances") or {}
    require(not any(bypass.get(key, []) for key in ("users", "teams", "apps")),
            "PR protection bypass is not supported")
    require(protection.get("allow_force_pushes", {}).get("enabled") is False
            and protection.get("allow_deletions", {}).get("enabled") is False,
            "force-push/delete bypass must be disabled")


def validate_environment(api, repository, branch, policy):
    """PR refs cannot consume the App token; required reviewers guard default runs."""
    prefix = f"repos/{repository}/environments/{CONTROL_ENVIRONMENT}"
    environment = api.get(prefix)
    require(environment.get("deployment_branch_policy") == {
        "protected_branches": False, "custom_branch_policies": True},
        "environment must allow only the explicit default branch")
    branches = api.pages(prefix + "/deployment-branch-policies", "branch_policies")
    require(len(branches) == 1 and branches[0].get("name") == branch
            and branches[0].get("type") == "branch", "PR/tag/wildcard environment access forbidden")
    rules = [rule for rule in environment.get("protection_rules", [])
             if rule.get("type") == "required_reviewers"]
    require(len(rules) == 1 and rules[0].get("prevent_self_review") is True,
            "environment requires non-self approval")
    reviewers = rules[0].get("reviewers", [])
    require(all(item.get("type") == "User" for item in reviewers)
            and sorted(item.get("reviewer", {}).get("id") for item in reviewers)
            == sorted(policy["reviewer_ids"]), "environment reviewers mismatch")
    validate_secret_confinement(api, repository, prefix)


def validate_secret_confinement(api, repository, environment_prefix):
    """Verify the named credential is environment-only, never a repository secret."""
    environment = api.pages(environment_prefix + "/secrets", "secrets", "name")
    repository_secrets = api.pages(f"repos/{repository}/actions/secrets", "secrets", "name")
    organization_secrets = api.pages(f"repos/{repository}/actions/organization-secrets", "secrets", "name")
    require(any(secret.get("name") == TOKEN_SECRET for secret in environment),
            "environment-only gate App token missing")
    require(not any(secret.get("name") == TOKEN_SECRET for secret in repository_secrets + organization_secrets),
            "gate credential must not be a repository-wide secret")


def validate_setup(api, repository, policy):
    """Reject shared tokens, missing permissions, broad writers or unsupported rules."""
    validate_control_policy(policy)
    installation = api.get("installation/repositories?per_page=100")
    require(installation.get("total_count") == 1
            and [item.get("full_name") for item in installation.get("repositories", [])] == [repository],
            "gate credential must be an installation token scoped to this repository only")
    metadata = api.get(f"repos/{repository}")
    require(metadata.get("allow_auto_merge") is False and metadata.get("allow_squash_merge") is True,
            "native auto-merge must be disabled and explicit squash merge permitted")
    branch = metadata.get("default_branch")
    require(isinstance(branch, str) and branch, "default branch unavailable")
    protection = api.get(f"repos/{repository}/branches/{quote(branch, safe='')}/protection")
    validate_branch(protection, policy)
    rulesets = api.pages(f"repos/{repository}/rulesets?includes_parents=true")
    require(not any(rule.get("enforcement") != "disabled" for rule in rulesets),
            "active rulesets require a separately reviewed prerequisite adapter")
    validate_environment(api, repository, branch, policy)
    return branch


def verify_custody(collector, base_revision, policy):
    """An independent administrator source must certify otherwise invisible custody."""
    check = collector.check(policy["custody_source"], base_revision, CUSTODY_MAX_AGE_SECONDS)
    record = load_json(check.get("output", {}).get("summary"))
    require(isinstance(record, dict) and record.get("exclusive_app_merge") is True
            and record == {"repository": collector.repository, "base_revision": base_revision,
                       "environment": CONTROL_ENVIRONMENT, "gate_app_id": policy["app_id"],
                       "credential_isolation": "environment_only", "exclusive_app_merge": True},
            "credential/destination custody certification missing or mismatched")
    return check["completed_at"]
