"""Bounded GitHub collector. Never execute evaluated repository code."""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import quote

from fabric_gate import (
    ARCHIVE_GATES,
    REPOSITORY_PATTERN,
    GateError,
    evaluate,
    fresh,
    load_json,
    require,
    revision,
)
from fabric_mapping import authorize_pair, mapping_snapshot, release_snapshot, verify_pr

PAGE_SIZE = 100
MAX_PAGES = 3
MAX_REQUESTS = 80
REQUEST_TIMEOUT_SECONDS = 20
COLLECTION_TIMEOUT_SECONDS = 120
MAX_RESPONSE_BYTES = 4 * 1024 * 1024
MAX_TAG_DEPTH = 3
TRUSTED_FILES = (
    ".github/skills/fabric-verify-change/scripts/fabric_gate.py",
    ".github/skills/fabric-verify-change/scripts/collect_fabric_evidence.py",
    ".github/skills/fabric-verify-change/scripts/gate-policy.json",
    ".github/skills/fabric-verify-change/scripts/fabric_mapping.py",
    ".github/skills/fabric-verify-change/scripts/fabric_control_policy.py",
    ".github/skills/fabric-verify-change/scripts/run_fabric_gate_control.py",
    ".github/skills/fabric-verify-change/scripts/gate-evidence.schema.json",
)
RUNTIME_PATH = Path(".github/skills/fabric-verify-change/scripts")


class GitHubAPI:
    """Authenticated, read-only API with explicit request and time bounds."""

    def __init__(self):
        self.requests = 0
        self.deadline = time.monotonic() + COLLECTION_TIMEOUT_SECONDS

    def get(self, endpoint):
        """Fail closed on API errors, timeouts, malformed or oversized responses."""
        self.requests += 1
        require(self.requests <= MAX_REQUESTS, "GitHub request budget exhausted")
        remaining = self.deadline - time.monotonic()
        require(remaining > 0, "GitHub collection deadline exceeded")
        try:
            response = subprocess.run(
                ["gh", "api", "--hostname", "github.com", "--method", "GET", endpoint],
                capture_output=True, timeout=min(REQUEST_TIMEOUT_SECONDS, remaining),
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            raise GateError("GitHub source unavailable or timed out") from error
        require(response.returncode == 0, "GitHub source unavailable or unauthorized")
        require(len(response.stdout) <= MAX_RESPONSE_BYTES, "GitHub response exceeds bound")
        try:
            return load_json(response.stdout.decode("utf-8"))
        except UnicodeError as error:
            raise GateError("GitHub response is not UTF-8") from error

    def pages(self, endpoint, field=None, identity_key="id"):
        """Read bounded pages without silently accepting truncated collections."""
        records = []
        separator = "&" if "?" in endpoint else "?"
        for page in range(1, MAX_PAGES + 1):
            response = self.get(f"{endpoint}{separator}per_page={PAGE_SIZE}&page={page}")
            batch = response.get(field) if field and isinstance(response, dict) else response
            require(isinstance(batch, list) and all(isinstance(item, dict) for item in batch),
                    "malformed GitHub collection")
            records.extend(batch)
            if len(batch) < PAGE_SIZE:
                identifiers = [record.get(identity_key) for record in records]
                require(all((type(value) is int and value > 0) if identity_key == "id"
                            else (isinstance(value, str) and value.strip()) for value in identifiers)
                        and len(set(identifiers)) == len(identifiers),
                        "missing or duplicate GitHub record IDs")
                return records
        raise GateError("GitHub collection exceeds pagination bound")


class Collector:
    """Evidence is fetched live from GitHub, not loaded from PR files."""

    def __init__(self, repository, api=None, now=None):
        require(isinstance(repository, str) and REPOSITORY_PATTERN.fullmatch(repository),
                "invalid repository")
        self.repository = repository
        self.api = api or GitHubAPI()
        self.now = now or datetime.now(UTC)
        self.cache = {}
        self.scope_time = None
        self.base_revision = None
        self.pr_author_id = None
        self.identity = ""
        self.review_identity = None
        self.archive_context = None
        self.config = None
        self.mapping_observation = None
        self.release_observation = None
        self.operational = None
        self.clock = (lambda: now) if now is not None else (lambda: datetime.now(UTC))

    def reference(self, collection, identifier):
        """Construct references instead of trusting author-controlled URLs."""
        require(type(identifier) is int and identifier > 0, "invalid evidence ID")
        return f"https://api.github.com/repos/{self.repository}/{collection}/{identifier}"

    def records(self, path, field=None):
        """Cache bounded reads for a single evaluation only."""
        if path not in self.cache:
            self.cache[path] = self.api.pages(f"repos/{self.repository}/{path}", field)
        return self.cache[path]

    def bind(self, lifecycle, revision_sha, identity):
        """Bind PR head to the current default/protected configuration base."""
        self.identity = identity
        if lifecycle == "merge":
            require(re.fullmatch(r"pr:[1-9][0-9]*", identity), "merge needs pr:<number>")
            self.verify_pr(revision_sha, identity)
        else:
            commit = self.api.get(f"repos/{self.repository}/commits/{revision_sha}")
            require(commit.get("sha") == revision_sha, "revision unavailable")
            if lifecycle == "archive":
                self.prepare_archive(revision_sha)

    def prepare_archive(self, revision_sha):
        """Mapping is authenticated before collecting gates for the deployed SHA."""
        context = self.archive_context
        require(context is not None, "archive context required")
        authorize_pair(self.config["mapping"], self.repository, context["deployed_repository"])
        if context["deployed_revision"] != revision_sha:
            self.mapping_observation = mapping_snapshot(self, self.config, revision_sha)
            verify_pr(self, revision_sha, False)
        elif context["release_id"] is not None:
            self.release_observation = release_snapshot(
                self.api, context["deployed_repository"], context["release_id"])

    def gate_revision(self, gate, revision_sha):
        """Operational gates bind to deployment; all change gates bind to evaluation."""
        if self.archive_context is not None and gate in ARCHIVE_GATES:
            return self.archive_context["deployed_revision"]
        return revision_sha

    def for_gate(self, gate):
        """Selected stores never determine evidence repositories."""
        if self.archive_context is None or gate not in ARCHIVE_GATES:
            return self
        if self.operational is None:
            self.operational = Collector(self.archive_context["deployed_repository"], self.api, self.now)
            self.operational.identity = self.identity
            self.operational.archive_context = self.archive_context
            self.operational.review_identity = self.review_identity
        return self.operational

    def verify_pr(self, revision_sha, identity):
        """Reject closed PRs, changed heads and alternate/untrusted base branches."""
        pull = self.api.get(f"repos/{self.repository}/pulls/{identity.split(':')[1]}")
        repository = self.api.get(f"repos/{self.repository}")
        base = pull.get("base", {})
        require(pull.get("state") == "open" and pull.get("head", {}).get("sha") == revision_sha,
                "PR is closed or current head changed")
        require(base.get("repo", {}).get("full_name") == self.repository
                and base.get("ref") == repository.get("default_branch"),
                "PR must target trusted default branch")
        self.pr_author_id = pull.get("user", {}).get("id")
        require(self.base_revision is None or base.get("sha") == self.base_revision,
                "protected base changed; rerun control")
        self.base_revision = base.get("sha")

    def recheck(self, lifecycle, revision_sha, identity, entries=None):
        """Close the collection window with a fresh current-head read."""
        if lifecycle == "merge":
            self.verify_pr(revision_sha, identity)
        elif lifecycle == "archive":
            self.archive_relation(revision_sha, entries)

    def archive_relation(self, revision_sha, entries):
        """Prove the explicit PR/release relation, not a caller's release assertion."""
        context = self.archive_context
        require(context is not None, "archive context required")
        self.now = self.clock()
        if self.mapping_observation is not None:
            self.cache.clear()
            current = mapping_snapshot(self, self.config, revision_sha)
            require(current == self.mapping_observation, "mapping/release/deployment changed during evaluation")
            verify_pr(self, revision_sha, False)
            return
        needs_release = any(entry["applicable"] for entry in entries
                            if entry["gate"] in {"deployment", "release_readiness"})
        if needs_release or context["release_id"] is not None:
            verify_pr(self, revision_sha, True)
            release_id = context["release_id"]
            require(type(release_id) is int and release_id > 0, "published release ID required")
            snapshot = release_snapshot(self.api, context["deployed_repository"], release_id)
            require(snapshot == self.release_observation, "release/tag changed during evaluation")
            resolved = snapshot["commit"]
            require(resolved == revision_sha == context["deployed_revision"],
                    "release/evaluated/deployed revision mismatch")
            context["release_revision"] = resolved
            context["release_reference"] = f"https://api.github.com/repos/{context['deployed_repository']}/releases/{release_id}"
        else:
            verify_pr(self, revision_sha, False)
        self.recheck_operations(entries)

    def recheck_operations(self, entries):
        """Requery mutable deployment status pointers before authorizing archive."""
        deployment = next(entry for entry in entries if entry["gate"] == "deployment")
        if deployment["applicable"]:
            operational = self.for_gate("deployment")
            operational.cache.clear()
            operational.now = self.now
            rule = self.config["lifecycles"]["archive"]["deployment"]
            reference, _ = operational.evidence(rule["source"],
                self.archive_context["deployed_revision"], rule["max_age_seconds"])
            require(reference == deployment["reference"], "deployment status changed during evaluation")

    def check(self, source, revision_sha, max_age):
        """Only one exact authorized app/name result may satisfy a gate."""
        checks = self.records(f"commits/{revision_sha}/check-runs?filter=all", "check_runs")
        matches = [check for check in checks if check.get("name") == source["name"]
                   and check.get("app", {}).get("id") == source["app_id"]]
        require(len(matches) == 1, f"missing or ambiguous check: {source['name']}")
        check = matches[0]
        require(isinstance(check["app"].get("slug"), str) and check["app"]["slug"]
                and check["app"]["slug"] != "github-actions",
                "GitHub Actions app/name alone cannot authenticate a protected workflow")
        require(check.get("head_sha") == revision_sha, "check revision mismatch")
        require(check.get("status") == "completed" and check.get("conclusion") == "success",
                f"failed, skipped, or waiting check: {source['name']}")
        fresh(check.get("completed_at"), self.now, max_age)
        if self.archive_context is not None:
            summary = load_json(check.get("output", {}).get("summary"))
            require(isinstance(summary, dict) and summary.get("identity") == self.identity,
                    "archive check store/change identity mismatch")
        self.scope_time = check["completed_at"]
        return check

    def review(self, source, revision_sha, max_age):
        """Gate-specific approvals, latest disposition per authorized reviewer."""
        identity = self.review_identity or self.identity
        require(re.fullmatch(r"pr:[1-9][0-9]*", identity),
                "review evidence requires PR identity")
        number = identity.split(":")[1]
        self.review_context(number, revision_sha)
        reviews = self.records(f"pulls/{number}/reviews")
        latest = {}
        for review in reviews:
            reviewer = review.get("user", {}).get("id")
            if (reviewer in source["reviewer_ids"] and reviewer != self.pr_author_id
                    and (reviewer not in latest or review["id"] > latest[reviewer]["id"])):
                latest[reviewer] = review
        valid = [review for review in latest.values()
                 if review.get("state") == "APPROVED" and review.get("commit_id") == revision_sha
                 and (not source["marker"] or review.get("body", "").strip() == source["marker"])]
        require(valid and not any(review.get("state") == "CHANGES_REQUESTED"
                                  for review in latest.values()), "missing/superseded gate review")
        selected = max(valid, key=lambda review: review["id"])
        fresh(selected.get("submitted_at"), self.now, max_age)
        return self.reference(f"pulls/{number}/reviews", selected["id"]), selected["submitted_at"]

    def review_context(self, number, revision_sha):
        """Exclude self-review and bind non-merge review contexts to the same head."""
        pull = self.api.get(f"repos/{self.repository}/pulls/{number}")
        require(pull.get("head", {}).get("sha") == revision_sha
                and pull.get("base", {}).get("repo", {}).get("full_name") == self.repository,
                "review PR revision/repository mismatch")
        self.pr_author_id = pull.get("user", {}).get("id")
        require(type(self.pr_author_id) is int and self.pr_author_id > 0,
                "PR author identity unavailable")

    def deployment(self, source, revision_sha, max_age):
        """Use exact deployed revision/environment and latest trusted disposition."""
        deployments = self.records(f"deployments?sha={revision_sha}")
        matches = [deployment for deployment in deployments
                   if deployment.get("sha") == revision_sha
                   and deployment.get("environment") == source["environment"]
                   and deployment.get("creator", {}).get("id") == source["creator_id"]]
        require(len(matches) == 1, "missing or ambiguous deployed revision")
        deployment = matches[0]
        statuses = self.records(f"deployments/{deployment['id']}/statuses")
        require(statuses, "deployment statuses unavailable")
        latest = max(statuses, key=lambda status: status["id"])
        require(latest.get("creator", {}).get("id") == source["status_creator_id"]
                and latest.get("state") == "success"
                and latest.get("environment") == source["environment"],
                "deployment failed, inactive, or unauthorized")
        fresh(latest.get("created_at"), self.now, max_age)
        return self.reference(f"deployments/{deployment['id']}/statuses", latest["id"]), latest[
            "created_at"]

    def evidence(self, source, revision_sha, max_age):
        """Return a verified reference and observation time, never copied content."""
        if source["kind"] == "check":
            check = self.check(source, revision_sha, max_age)
            return self.reference("check-runs", check["id"]), check["completed_at"]
        if source["kind"] == "review":
            return self.review(source, revision_sha, max_age)
        return self.deployment(source, revision_sha, max_age)

def trusted_checkout(root, repository, api, expected_base=None):
    """Require clean owned inputs at the current default-branch SHA."""
    metadata = api.get(f"repos/{repository}")
    branch = metadata.get("default_branch")
    require(isinstance(branch, str) and re.fullmatch(r"[A-Za-z0-9_./-]+", branch),
            "invalid trusted branch")
    protected = api.get(f"repos/{repository}/branches/{quote(branch, safe='')}")
    require(protected.get("protected") is True, "default branch protection unavailable/unset")
    base = protected.get("commit", {}).get("sha")
    revision(base)
    if expected_base:
        require(base == expected_base, "trusted default branch changed")
    head = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                          capture_output=True, text=True, check=False)
    require(head.returncode == 0 and head.stdout.strip() == base, "not a trusted base checkout")
    status = subprocess.run(["git", "-C", str(root), "status", "--porcelain", "--",
                             *TRUSTED_FILES], capture_output=True, text=True, check=False)
    require(status.returncode == 0 and not status.stdout.strip(), "modified trusted inputs")
    return base


def resolve_release_revision(api, repository, release):
    """Resolve an existing release tag to a commit without trusting target_commitish."""
    tag = release.get("tag_name")
    require(isinstance(tag, str) and tag.strip(), "release tag required")
    reference = api.get(f"repos/{repository}/git/ref/tags/{quote(tag, safe='')}")
    commit = reference.get("object", {})
    for _ in range(MAX_TAG_DEPTH):
        if commit.get("type") == "commit":
            revision(commit.get("sha"))
            return commit["sha"]
        require(commit.get("type") == "tag", "release tag is not a commit")
        revision(commit.get("sha"))
        commit = api.get(f"repos/{repository}/git/tags/{commit['sha']}").get("object", {})
    raise GateError("release tag nesting exceeds bound")


def validate_archive_context(lifecycle, revision_sha, deployed_revision, change, identity,
                             store=None, pr_number=None, release_id=None, deployed_repository=None):
    """An archive result never maps an unrelated commit to a deployed revision."""
    if lifecycle == "archive":
        revision(deployed_revision)
        require(isinstance(deployed_repository, str) and REPOSITORY_PATTERN.fullmatch(deployed_repository),
                "explicit deployed repository required")
        require(isinstance(change, str) and re.fullmatch(r"[a-z0-9][a-z0-9-]*", change),
                "archive change slug required")
        require(isinstance(store, str) and re.fullmatch(r"local|store:[A-Za-z0-9_.-]+", store),
                "explicit archive store identity required")
        require(identity == f"change:{store}:{change}", "archive identity mismatch")
        require(isinstance(pr_number, str) and re.fullmatch(r"[1-9][0-9]*", pr_number),
                "explicit archive PR required")
        require(release_id is None or (isinstance(release_id, str)
                and re.fullmatch(r"[1-9][0-9]*", release_id)), "invalid release ID")
        return {"store": store, "change": change, "pr": int(pr_number),
                "release_id": int(release_id) if release_id else None,
                "deployed_revision": deployed_revision, "release_revision": None,
                "release_reference": None, "deployed_repository": deployed_repository, "mapping": None}
    return None


def preflight(root, repository, lifecycle, revision_sha, identity, api=None, now=None,
              deployed_revision=None, change=None, pr_number=None, store=None, release_id=None,
              deployed_repository=None):
    """Parent interface: call BEFORE any sync writes/moves; failure raises GateError."""
    require(isinstance(repository, str) and REPOSITORY_PATTERN.fullmatch(repository),
            "invalid repository")
    context = validate_archive_context(lifecycle, revision_sha, deployed_revision, change, identity,
                                       store, pr_number, release_id, deployed_repository)
    api = api or GitHubAPI()
    base = trusted_checkout(root, repository, api)
    config = load_json((root / RUNTIME_PATH / "gate-policy.json").read_text(encoding="utf-8"))
    collector = Collector(repository, api, now)
    collector.archive_context = context
    collector.review_identity = f"pr:{pr_number}" if pr_number else identity
    if lifecycle == "merge":
        collector.base_revision = base
    manifest = evaluate(config, collector, lifecycle, revision_sha, identity, base)
    trusted_checkout(root, repository, api, base)
    from fabric_gate import validate_manifest

    validate_manifest(manifest, config, lifecycle, revision_sha, identity, collector.clock())
    return manifest


def parse_arguments():
    """Inputs are identities only, never executable code or a supplied manifest."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY"))
    parser.add_argument("--lifecycle", choices=("merge", "release", "archive"), required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--identity")
    parser.add_argument("--deployed-revision")
    parser.add_argument("--change")
    parser.add_argument("--pr")
    parser.add_argument("--store")
    parser.add_argument("--release-id")
    parser.add_argument("--deployed-repository")
    return parser.parse_args()


def main():
    """Print a non-sensitive status to stdout; never expose manifest contents."""
    arguments = parse_arguments()
    try:
        root = Path(__file__).resolve().parents[4]
        identity = arguments.identity
        if identity is None:
            identity = f"change:{arguments.store}:{arguments.change}" if arguments.lifecycle == "archive" else (
                f"pr:{arguments.pr}" if arguments.pr else "")
        manifest = preflight(root, arguments.repository, arguments.lifecycle,
                             arguments.revision, identity,
                             deployed_revision=arguments.deployed_revision,
                             change=arguments.change, pr_number=arguments.pr,
                             store=arguments.store, release_id=arguments.release_id or None,
                             deployed_repository=arguments.deployed_repository)
        print(json.dumps({"status": "ok"}))
        return 0
    except (GateError, OSError, KeyError, TypeError) as error:
        print(f"Fabric gate blocked: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
