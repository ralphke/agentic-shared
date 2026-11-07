"""Gate-only App checks and explicitly requested, head-conditional operations."""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

from collect_fabric_evidence import (
    MAX_REQUESTS,
    MAX_RESPONSE_BYTES,
    Collector,
    GitHubAPI,
    preflight,
    trusted_checkout,
)
from fabric_control_policy import (
    CUSTODY_MAX_AGE_SECONDS,
    validate_setup,
    verify_custody,
)
from fabric_gate import (
    REPOSITORY_PATTERN,
    GateError,
    fresh,
    load_json,
    require,
    revision,
    validate_config,
    validate_manifest,
)

WRITE_TIMEOUT_SECONDS = 20
RUNTIME = Path(".github/skills/fabric-verify-change/scripts")


class ControlAPI(GitHubAPI):
    """Bounded mutations; credentials are never supplied by evaluated PR code."""

    def mutate(self, endpoint, fields, method="POST"):
        self.requests += 1
        require(self.requests <= MAX_REQUESTS, "GitHub mutation budget exhausted")
        remaining = self.deadline - time.monotonic()
        require(remaining > 0, "GitHub mutation deadline exceeded")
        try:
            response = subprocess.run(
                ["gh", "api", "--hostname", "github.com", "--method", method,
                 endpoint, "--input", "-"], input=json.dumps(fields).encode(),
                capture_output=True, timeout=min(WRITE_TIMEOUT_SECONDS, remaining), check=False)
        except (OSError, subprocess.TimeoutExpired) as error:
            raise GateError("GitHub mutation unavailable or timed out") from error
        require(response.returncode == 0, "GitHub mutation failed")
        require(len(response.stdout) <= MAX_RESPONSE_BYTES, "GitHub mutation response exceeds bound")
        try:
            return load_json(response.stdout.decode("utf-8"))
        except UnicodeError as error:
            raise GateError("GitHub mutation response is not UTF-8") from error


def check_identity(check, policy, name, revision_sha):
    """App provenance is authenticated from the server, not token names or claims."""
    require(isinstance(check, dict) and isinstance(check.get("app"), dict), "malformed verdict identity")
    require(check["app"].get("id") == policy["app_id"]
            and isinstance(check["app"].get("slug"), str)
            and check.get("app", {}).get("slug") not in (None, "", "github-actions")
            and check.get("name") == name and check.get("head_sha") == revision_sha
            and type(check.get("id")) is int and check["id"] > 0,
            "verdict must originate from the unique gate-only App")


def start_check(api, repository, revision_sha, name, policy):
    """A shared GITHUB_TOKEN can never publish a passing required-source verdict."""
    check = api.mutate(f"repos/{repository}/check-runs",
                       {"name": name, "head_sha": revision_sha, "status": "in_progress"})
    check_identity(check, policy, name, revision_sha)
    return check["id"]


def finish_check(api, repository, identifier, revision_sha, name, policy, conclusion):
    """Publish only to an already authenticated gate-only App check."""
    check = api.mutate(f"repos/{repository}/check-runs/{identifier}",
        {"status": "completed", "conclusion": conclusion,
         "completed_at": datetime.now(UTC).isoformat().replace("+00:00", "Z")}, "PATCH")
    check_identity(check, policy, name, revision_sha)
    require(check["id"] == identifier and check.get("conclusion") == conclusion,
            "verdict update identity mismatch")


def protected_policy(root, repository, api):
    """Validate current protected bootstrap, native restrictions and credential custody."""
    base = trusted_checkout(root, repository, api)
    policy = load_json((root / RUNTIME / "gate-policy.json").read_text(encoding="utf-8"))
    validate_config(policy)
    require(policy["repository"] == repository, "controller repository mismatch")
    validate_setup(api, repository, policy["control"])
    api.custody_observed_at = verify_custody(Collector(repository, api), base, policy["control"])
    return policy


def current_pull(api, repository, number, expected_head=None):
    """Explicit operation input cannot choose an outdated or unrelated head."""
    require(isinstance(number, str) and re.fullmatch(r"[1-9][0-9]*", number), "invalid PR number")
    pull = api.get(f"repos/{repository}/pulls/{number}")
    revision_sha = pull.get("head", {}).get("sha")
    revision(revision_sha)
    require(pull.get("state") == "open", "PR is not open")
    if expected_head is not None:
        revision(expected_head)
        require(expected_head == revision_sha, "requested merge head changed")
    return pull, revision_sha


def merge_control(root, repository, number, api, expected_head=None, execute=False):
    """Only an explicit request takes the protected merge path; no surprise auto-merge."""
    require(not execute or expected_head is not None, "explicit merge requires expected head")
    _, revision_sha = current_pull(api, repository, number, expected_head)
    policy = protected_policy(root, repository, api)
    identifier = start_check(api, repository, revision_sha, "Fabric / merge", policy["control"])
    try:
        manifest = preflight(root, repository, "merge", revision_sha, f"pr:{number}", api)
        finish_check(api, repository, identifier, revision_sha, "Fabric / merge",
                     policy["control"], "success")
        if execute:
            merge_at_boundary(root, repository, number, revision_sha, api, policy)
        print(json.dumps(manifest, sort_keys=True))
    except (GateError, OSError, KeyError, TypeError):
        finish_check(api, repository, identifier, revision_sha, "Fabric / merge",
                     policy["control"], "failure")
        raise


def merge_at_boundary(root, repository, number, revision_sha, api, policy):
    """Do not authorize mutation from a previous verdict or manifest."""
    current = protected_policy(root, repository, api)
    require(current == policy, "protected controller policy changed")
    manifest = preflight(root, repository, "merge", revision_sha, f"pr:{number}", api)
    require(protected_policy(root, repository, api) == policy, "destination prerequisites changed")
    validate_manifest(manifest, policy, "merge", revision_sha, f"pr:{number}", datetime.now(UTC))
    fresh(getattr(api, "custody_observed_at", None), datetime.now(UTC), CUSTODY_MAX_AGE_SECONDS)
    response = api.mutate(f"repos/{repository}/pulls/{number}/merge",
                         {"sha": revision_sha, "merge_method": "squash"}, "PUT")
    require(response.get("merged") is True, "GitHub refused the protected conditional merge")


def release_snapshot(api, repository, release_id):
    """Resolve an existing draft tag, not mutable target_commitish."""
    from collect_fabric_evidence import resolve_release_revision

    draft = api.get(f"repos/{repository}/releases/{release_id}")
    require(draft.get("id") == release_id and draft.get("draft") is True, "existing draft required")
    return draft, resolve_release_revision(api, repository, draft)


def release_control(root, repository, identifier, api):
    """Gate the intended publication operation; not every independently authorized API."""
    require(re.fullmatch(r"[1-9][0-9]*", identifier), "invalid release ID")
    original, revision_sha = release_snapshot(api, repository, int(identifier))
    policy = protected_policy(root, repository, api)
    check_id = start_check(api, repository, revision_sha, "Fabric / release", policy["control"])
    try:
        manifest = preflight(root, repository, "release", revision_sha, f"release:{identifier}", api)
        require(release_snapshot(api, repository, int(identifier)) == (original, revision_sha),
                "draft release or tag changed during evaluation")
        require(protected_policy(root, repository, api) == policy, "publication prerequisites changed")
        validate_manifest(manifest, policy, "release", revision_sha, f"release:{identifier}",
                          datetime.now(UTC))
        finish_check(api, repository, check_id, revision_sha, "Fabric / release",
                     policy["control"], "success")
        api.mutate(f"repos/{repository}/releases/{identifier}", {"draft": False}, "PATCH")
        print(json.dumps(manifest, sort_keys=True))
    except (GateError, OSError, KeyError, TypeError):
        finish_check(api, repository, check_id, revision_sha, "Fabric / release",
                     policy["control"], "failure")
        raise


def invalidate(root, repository, api, number=None):
    """Best-effort supplementary revocation; it never requests a merge."""
    policy = protected_policy(root, repository, api)
    pulls = [current_pull(api, repository, number)[0]] if number else api.pages(
        f"repos/{repository}/pulls?state=open")
    for pull in pulls:
        revision_sha = pull.get("head", {}).get("sha")
        revision(revision_sha)
        runs = api.pages(f"repos/{repository}/commits/{revision_sha}/check-runs?filter=all", "check_runs")
        for check in runs:
            if check.get("name") == "Fabric / merge" and check.get("app", {}).get("id") == policy["control"]["app_id"]:
                finish_check(api, repository, check["id"], revision_sha, "Fabric / merge",
                             policy["control"], "failure")


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("merge", "release", "invalidate"), required=True)
    parser.add_argument("--number")
    parser.add_argument("--expected-head")
    parser.add_argument("--execute-merge", action="store_true")
    return parser.parse_args()


def main():
    """No privileged execution of evaluated code; no live operation by this agent."""
    options = arguments()
    try:
        repository = os.environ.get("GITHUB_REPOSITORY", "")
        require(REPOSITORY_PATTERN.fullmatch(repository), "invalid repository")
        root = Path(__file__).resolve().parents[4]
        api = ControlAPI()
        if options.mode == "merge":
            merge_control(root, repository, options.number, api, options.expected_head, options.execute_merge)
        elif options.mode == "release":
            require(not options.execute_merge, "merge option invalid for release")
            release_control(root, repository, options.number, api)
        else:
            require(not options.execute_merge, "revocation cannot request a merge")
            invalidate(root, repository, api, options.number)
        return 0
    except (GateError, OSError, KeyError, TypeError) as error:
        print(f"Fabric control blocked: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
