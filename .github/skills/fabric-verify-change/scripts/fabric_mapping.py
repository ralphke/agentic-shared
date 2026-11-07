"""Bounded external change/deployment binding; never infer a link from ancestry."""

import hashlib
import json
from urllib.parse import quote

from fabric_gate import (
    MAX_AGE_SECONDS,
    REPOSITORY_PATTERN,
    GateError,
    exact_fields,
    fresh,
    load_json,
    require,
    revision,
    timestamp,
    validate_source,
)

MAX_TAG_DEPTH = 3
MAPPING_GATE = "change_deployment_mapping"


def validate_mapping_policy(policy):
    """An absent adapter never permits different revisions or repository inference."""
    if policy is None:
        return
    exact_fields(policy, {"source", "max_age_seconds", "repository_pairs"}, "mapping policy")
    validate_source(policy["source"], MAPPING_GATE)
    require(policy["source"]["kind"] == "check", "mapping requires a dedicated check app")
    require(type(policy["max_age_seconds"]) is int
            and 0 < policy["max_age_seconds"] <= MAX_AGE_SECONDS, "invalid mapping freshness")
    pairs = policy["repository_pairs"]
    require(isinstance(pairs, list) and pairs, "explicit mapping repository pairs required")
    identities = []
    for pair in pairs:
        exact_fields(pair, {"evaluated", "deployed"}, "repository pair")
        require(all(isinstance(value, str) and REPOSITORY_PATTERN.fullmatch(value)
                    for value in pair.values()), "invalid mapping repository pair")
        identities.append((pair["evaluated"], pair["deployed"]))
    require(len(identities) == len(set(identities)), "duplicate mapping repository pair")


def authorize_pair(policy, evaluated_repository, deployed_repository):
    """Repository relationships come only from protected policy."""
    if evaluated_repository == deployed_repository:
        return
    require(policy is not None and {"evaluated": evaluated_repository,
            "deployed": deployed_repository} in policy["repository_pairs"],
            "deployment repository relationship is not authorized")


def release_snapshot(api, repository, release_id):
    """Snapshot mutable release metadata, ref object and peeled commit independently."""
    require(type(release_id) is int and release_id > 0, "published release ID required")
    release = api.get(f"repos/{repository}/releases/{release_id}")
    require(release.get("id") == release_id and release.get("draft") is False
            and release.get("published_at"), "published release required")
    tag = release.get("tag_name")
    require(isinstance(tag, str) and tag.strip(), "release tag required")
    reference = api.get(f"repos/{repository}/git/ref/tags/{quote(tag, safe='')}")
    tag_object = reference.get("object", {})
    revision(tag_object.get("sha"))
    commit = tag_object
    for _ in range(MAX_TAG_DEPTH):
        if commit.get("type") == "commit":
            revision(commit.get("sha"))
            return {"release": release, "tag": tag_object, "commit": commit["sha"]}
        require(commit.get("type") == "tag", "release tag is not a commit")
        revision(commit.get("sha"))
        commit = api.get(f"repos/{repository}/git/tags/{commit['sha']}").get("object", {})
    raise GateError("release tag nesting exceeds bound")


def deployment_snapshot(api, repository, deployment_id, status_id, source, deployed_sha, now, age):
    """Verify exact immutable IDs against the current latest status and creators."""
    deployment = api.get(f"repos/{repository}/deployments/{deployment_id}")
    require(deployment.get("id") == deployment_id and deployment.get("sha") == deployed_sha
            and deployment.get("environment") == source["environment"]
            and deployment.get("creator", {}).get("id") == source["creator_id"],
            "mapping deployment mismatch or unauthorized creator")
    statuses = api.pages(f"repos/{repository}/deployments/{deployment_id}/statuses")
    require(statuses, "mapping deployment statuses unavailable")
    latest = max(statuses, key=lambda status: status["id"])
    require(latest.get("id") == status_id and latest.get("state") == "success"
            and latest.get("environment") == source["environment"]
            and latest.get("creator", {}).get("id") == source["status_creator_id"],
            "mapping status is superseded, unsuccessful or unauthorized")
    fresh(latest.get("created_at"), now, age)
    return {"deployment": deployment, "status": latest}


def validate_record(record, collector, revision_sha, policy):
    """Strict producer payload; source authentication is outside this payload."""
    exact_fields(record, {"schema_version", "gate", "identity", "evaluated_repository",
                          "evaluated_revision", "deployed_repository", "deployed_revision",
                          "pull_request", "release", "deployment", "observed_at", "expires_at"},
                 MAPPING_GATE)
    context = collector.archive_context
    require(type(record["schema_version"]) is int and record["schema_version"] == 1
            and record["gate"] == MAPPING_GATE, "unsupported mapping schema/gate")
    expected = {"identity": collector.identity, "evaluated_repository": collector.repository,
                "evaluated_revision": revision_sha, "deployed_repository": context["deployed_repository"],
                "deployed_revision": context["deployed_revision"]}
    require(all(record[key] == value for key, value in expected.items()), "mapping identity mismatch")
    authorize_pair(policy, collector.repository, context["deployed_repository"])
    require({"evaluated": collector.repository, "deployed": context["deployed_repository"]}
            in policy["repository_pairs"], "mapping repository pair not configured")
    fresh(record["observed_at"], collector.now, policy["max_age_seconds"])
    expiry = timestamp(record["expires_at"])
    lifetime = (expiry - timestamp(record["observed_at"])).total_seconds()
    require(collector.now < expiry and 0 < lifetime <= policy["max_age_seconds"],
            "mapping expired or excessive lifetime")
    exact_fields(record["pull_request"], {"repository", "number", "evaluated_revision"}, "mapping PR")
    require(type(record["pull_request"]["number"]) is int
            and record["pull_request"] == {"repository": collector.repository, "number": context["pr"],
                                      "evaluated_revision": revision_sha}, "mapping PR mismatch")


def verify_record_links(record, collector, source, age):
    """Retrieve every linked object independently, not from the check payload."""
    context = collector.archive_context
    release = record["release"]
    exact_fields(release, {"repository", "id", "tag_object_sha", "commit_sha"}, "mapping release")
    require(release["repository"] == context["deployed_repository"]
            and release["id"] == context["release_id"], "mapping release identity mismatch")
    snapshot = release_snapshot(collector.api, release["repository"], release["id"])
    require(snapshot["tag"]["sha"] == release["tag_object_sha"]
            and snapshot["commit"] == release["commit_sha"] == context["deployed_revision"],
            "mapping release/tag revision mismatch")
    deployment = record["deployment"]
    exact_fields(deployment, {"repository", "id", "status_id", "environment", "revision"},
                 "mapping deployment")
    require(deployment["repository"] == context["deployed_repository"]
            and deployment["environment"] == source["environment"]
            and deployment["revision"] == context["deployed_revision"],
            "mapping deployment identity mismatch")
    require(all(type(deployment[key]) is int and deployment[key] > 0 for key in ("id", "status_id")),
            "invalid mapping deployment/status ID")
    observed = deployment_snapshot(collector.api, deployment["repository"], deployment["id"],
                                   deployment["status_id"], source, deployment["revision"],
                                   collector.now, age)
    return {"release": snapshot, "deployment": observed}


def mapping_snapshot(collector, config, revision_sha):
    """Collect exactly one authorized mapping check on the evaluated revision."""
    policy = config["mapping"]
    require(policy is not None, "different revisions require configured trusted mapping")
    check = collector.check(policy["source"], revision_sha, policy["max_age_seconds"])
    record = load_json(check.get("output", {}).get("summary"))
    validate_record(record, collector, revision_sha, policy)
    source = config["lifecycles"]["archive"]["deployment"]["source"]
    require(source["kind"] == "deployment", "mapping needs exact deployment creator policy")
    links = verify_record_links(record, collector, source, policy["max_age_seconds"])
    digest = hashlib.sha256(json.dumps(record, sort_keys=True).encode()).hexdigest()
    context = collector.archive_context
    context["mapping"] = {"source": policy["source"],
                          "reference": collector.reference("check-runs", check["id"]),
                          "observed_at": record["observed_at"], "expires_at": record["expires_at"],
                          "record_sha256": digest, "completed_at": check["completed_at"]}
    context["release_revision"] = links["release"]["commit"]
    context["release_reference"] = f"https://api.github.com/repos/{context['deployed_repository']}" \
        f"/releases/{context['release_id']}"
    return {"record": record, "links": links, "check_id": check["id"]}


def verify_pr(collector, revision_sha, same_revision):
    """The PR must independently identify the evaluated SHA; no ancestry fallback."""
    context = collector.archive_context
    pull = collector.api.get(f"repos/{collector.repository}/pulls/{context['pr']}")
    require(pull.get("base", {}).get("repo", {}).get("full_name") == collector.repository,
            "archive PR repository mismatch")
    if same_revision:
        require(pull.get("merged") is True and pull.get("merge_commit_sha") == revision_sha,
                "archive revision is not the linked PR's merged revision")
    else:
        require(pull.get("merged") is True, "mapping PR must be merged")
        require(pull.get("head", {}).get("sha") == revision_sha
                or pull.get("merge_commit_sha") == revision_sha, "mapping evaluated PR mismatch")
    return pull
