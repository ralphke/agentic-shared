"""Fail-closed Fabric evidence evaluation; inputs must come from a trusted runner."""

import hashlib
import json
import re
from datetime import UTC, datetime

SCHEMA_VERSION = 1
MAX_AGE_SECONDS = 86400
FUTURE_SKEW_SECONDS = 60
LIFECYCLES = ("merge", "release", "archive")
SELF_CHECKS = {"Fabric / merge", "Fabric / release", "Fabric / archive"}
PRE_GATES = {
    "planning", "acceptance", "tasks", "scenarios", "ci", "security",
    "coverage", "code_review", "spec", "legal",
}
ARCHIVE_GATES = {
    "deployment", "slo", "alerts", "runbook", "stability", "postmortem",
}
SHA_PATTERN = re.compile(r"[0-9a-f]{40}")
REPOSITORY_PATTERN = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")
ARCHIVE_CONTEXT_FIELDS = {"store", "change", "pr", "release_id", "deployed_revision",
                         "release_revision", "release_reference", "deployed_repository", "mapping"}


class GateError(ValueError):
    """Evidence cannot authorize progression."""


def require(condition, message):
    """Reject invalid, missing, or ambiguous evidence."""
    if not condition:
        raise GateError(message)


def unique_object(pairs):
    """Reject duplicate JSON keys instead of silently overwriting them."""
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(text):
    """Load strict JSON without duplicate keys or nonfinite numbers."""
    try:
        return json.loads(text, object_pairs_hook=unique_object,
                          parse_constant=lambda value: require(False, f"invalid {value}"))
    except (ValueError, TypeError) as error:
        raise GateError(f"malformed JSON: {error}") from error


def exact_fields(value, fields, label):
    """Require an object with exactly the documented fields."""
    require(isinstance(value, dict) and set(value) == set(fields),
            f"{label}: missing or unknown fields")


def timestamp(value):
    """Require timezone-aware UTC timestamps."""
    require(isinstance(value, str) and "T" in value and value.endswith("Z"),
            "timestamp must be UTC")
    try:
        return datetime.fromisoformat(value)
    except ValueError as error:
        raise GateError("malformed timestamp") from error


def fresh(value, now, max_age):
    """Disallow future and expired evidence."""
    age = (now - timestamp(value)).total_seconds()
    require(-FUTURE_SKEW_SECONDS <= age <= max_age, "stale or future evidence")


def revision(value):
    """Validate a full immutable Git commit identity."""
    require(isinstance(value, str) and SHA_PATTERN.fullmatch(value), "invalid revision")


def required_gates(lifecycle):
    """Preserve pre-merge gates through all subsequent lifecycle points."""
    require(lifecycle in LIFECYCLES, "unknown lifecycle")
    gates = PRE_GATES.copy()
    if lifecycle != "merge":
        gates.add("release_readiness")
    if lifecycle == "archive":
        gates.update(ARCHIVE_GATES)
    return gates


def validate_source(source, gate):
    """Authenticate source identities by exact app/check or reviewer IDs."""
    require(isinstance(source, dict), f"{gate}: invalid source")
    kind = source.get("kind")
    if kind == "check":
        exact_fields(source, {"kind", "app_id", "name"}, gate)
        require(type(source["app_id"]) is int and source["app_id"] > 0,
                f"{gate}: configure a trusted app ID")
        require(isinstance(source["name"], str) and source["name"].strip()
                and source["name"] not in SELF_CHECKS, f"{gate}: invalid/self check")
    elif kind == "review":
        exact_fields(source, {"kind", "reviewer_ids", "marker"}, gate)
        reviewers = source["reviewer_ids"]
        require(isinstance(reviewers, list) and reviewers
                and all(type(value) is int and value > 0 for value in reviewers)
                and len(set(reviewers)) == len(reviewers), f"{gate}: invalid reviewers")
        marker = source["marker"]
        require(marker == f"fabric-gate:{gate}:approved"
                or (gate == "code_review" and marker == ""), f"{gate}: invalid marker")
    else:
        require(kind == "deployment" and gate == "deployment", f"{gate}: unknown source")
        exact_fields(source, {"kind", "environment", "creator_id", "status_creator_id"}, gate)
        require(isinstance(source["environment"], str) and source["environment"].strip(),
                "deployment: environment required")
        require(all(type(source[key]) is int and source[key] > 0
                    for key in ("creator_id", "status_creator_id")), "deployment: IDs required")


def validate_rule(rule, gate):
    """Validate scope rules; missing scope evidence always blocks."""
    exact_fields(rule, {"source", "scope", "max_age_seconds"}, gate)
    validate_source(rule["source"], gate)
    age = rule["max_age_seconds"]
    require(type(age) is int and 0 < age <= MAX_AGE_SECONDS, f"{gate}: invalid freshness")
    scope = rule["scope"]
    if scope is not None:
        exact_fields(scope, {"source", "allowed_rules"}, f"{gate} scope")
        validate_source(scope["source"], gate)
        require(scope["source"]["kind"] == "check", "scope requires a trusted check")
        allowed = scope["allowed_rules"]
        require(isinstance(allowed, dict) and allowed and all(
            isinstance(key, str) and key.strip() and isinstance(value, str) and value.strip()
            for key, value in allowed.items()), f"{gate}: invalid scope rules")
        require(gate in {"coverage", "legal", "release_readiness"} | ARCHIVE_GATES,
                f"{gate}: mandatory gate cannot be waived")


def validate_config(config):
    """Prevent omitted lifecycle gates or unconfigured identities from passing."""
    exact_fields(config, {"schema_version", "repository", "manifest_max_age_seconds",
                          "lifecycles", "mapping", "control"}, "configuration")
    require(type(config["schema_version"]) is int
            and config["schema_version"] == SCHEMA_VERSION, "unsupported config schema")
    require(isinstance(config["repository"], str)
            and REPOSITORY_PATTERN.fullmatch(config["repository"]), "invalid repository")
    age = config["manifest_max_age_seconds"]
    require(type(age) is int and 0 < age <= MAX_AGE_SECONDS, "invalid manifest freshness")
    validate_integrations(config)
    exact_fields(config["lifecycles"], LIFECYCLES, "lifecycles")
    for lifecycle, gates in config["lifecycles"].items():
        exact_fields(gates, required_gates(lifecycle), lifecycle)
        identities = []
        for gate, rule in gates.items():
            validate_rule(rule, gate)
            identities.append(json.dumps(rule["source"], sort_keys=True))
        require(len(identities) == len(set(identities)), f"{lifecycle}: reused gate source")


def validate_integrations(config):
    """Protected adapter configuration is mandatory, even when the CLI is read-only."""
    from fabric_control_policy import validate_control_policy
    from fabric_mapping import validate_mapping_policy

    validate_control_policy(config["control"])
    validate_mapping_policy(config["mapping"])


def config_digest(config):
    """Bind generated evidence to the trusted configuration."""
    return hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()


def applicability(collector, gate, rule, revision_sha, lifecycle):
    """Derive optionality from an authenticated, revision-bound scope check."""
    if rule["scope"] is None:
        return True, None, None
    scope = rule["scope"]
    check = collector.check(scope["source"], revision_sha, rule["max_age_seconds"])
    disposition = load_json(check.get("output", {}).get("summary"))
    fields = {"gate", "revision", "lifecycle", "required", "scope_rule", "reason"}
    if lifecycle == "archive":
        fields.add("identity")
    exact_fields(disposition, fields, f"{gate} scope disposition")
    require(disposition["gate"] == gate and disposition["revision"] == revision_sha
            and disposition["lifecycle"] == lifecycle, f"{gate}: mismatched scope")
    require(type(disposition["required"]) is bool, f"{gate}: ambiguous applicability")
    if disposition["required"]:
        require(disposition["scope_rule"] is None and disposition["reason"] is None,
                f"{gate}: contradictory scope")
    else:
        require(isinstance(disposition["scope_rule"], str)
                and disposition["scope_rule"] in scope["allowed_rules"],
                f"{gate}: trusted scope rule required")
        require(disposition["reason"] == scope["allowed_rules"][disposition["scope_rule"]],
                f"{gate}: configured scope-backed reason required")
    return disposition["required"], disposition, collector.reference("check-runs", check["id"])


def gate_entry(collector, gate, rule, revision_sha, lifecycle):
    """Collect one gate, never accepting an author-supplied manifest."""
    try:
        applicable, scope, scope_ref = applicability(
            collector, gate, rule, revision_sha, lifecycle)
        scope_observed_at = collector.scope_time if scope is not None else None
        reference, observed_at = collector.evidence(rule["source"], revision_sha,
                                                    rule["max_age_seconds"]) if applicable else (
                                                        scope_ref, collector.scope_time)
        return {"gate": gate, "applicable": applicable,
                "status": "passed" if applicable else "not_applicable",
                "revision": revision_sha, "source": rule["source"] if applicable else
                rule["scope"]["source"], "reference": reference, "observed_at": observed_at,
                "scope": scope, "scope_reference": scope_ref, "scope_observed_at": scope_observed_at}
    except (GateError, KeyError, TypeError) as error:
        raise GateError(f"{gate}: {error}") from error


def evaluate(config, collector, lifecycle, revision_sha, identity, trusted_base_sha):
    """Return an externally generated manifest or raise before any mutation."""
    validate_config(config)
    required_gates(lifecycle)
    revision(revision_sha)
    revision(trusted_base_sha)
    require(collector.repository == config["repository"], "repository mismatch")
    require(isinstance(identity, str) and identity.strip(), "change/PR identity required")
    collector.config = config
    collector.bind(lifecycle, revision_sha, identity)
    entries = [gate_entry(collector.for_gate(gate), gate, rule,
                         collector.gate_revision(gate, revision_sha), lifecycle)
               for gate, rule in sorted(config["lifecycles"][lifecycle].items())]
    collector.recheck(lifecycle, revision_sha, identity, entries)
    manifest = {"schema_version": SCHEMA_VERSION, "repository": config["repository"],
                "identity": identity, "lifecycle": lifecycle, "revision": revision_sha,
                "trusted_base_revision": trusted_base_sha, "config_sha256": config_digest(config),
                "generated_at": collector.now.isoformat().replace("+00:00", "Z"),
                "gates": entries, "archive_context": collector.archive_context}
    validate_manifest(manifest, config, lifecycle, revision_sha, identity, collector.now)
    return manifest


def validate_entry(entry, config, lifecycle, revision_sha, now, repository=None):
    """Validate schema and authorization, not provenance of an offline claim."""
    exact_fields(entry, {"gate", "applicable", "status", "revision", "source", "reference",
                         "observed_at", "scope", "scope_reference", "scope_observed_at"}, "manifest gate")
    gate = entry["gate"]
    rule = config["lifecycles"][lifecycle][gate]
    require(type(entry["applicable"]) is bool, f"{gate}: ambiguous applicability")
    require(entry["revision"] == revision_sha, f"{gate}: revision mismatch")
    expected = "passed" if entry["applicable"] else "not_applicable"
    require(entry["status"] == expected, f"{gate}: failed/unknown status")
    source = rule["source"] if entry["applicable"] else (rule["scope"] or {}).get("source")
    require(source is not None and entry["source"] == source, f"{gate}: unauthorized source")
    prefix = f"https://api.github.com/repos/{config['repository']}/"
    if repository is not None:
        prefix = f"https://api.github.com/repos/{repository}/"
    suffix = {"check": r"check-runs/[1-9][0-9]*",
              "review": r"pulls/[1-9][0-9]*/reviews/[1-9][0-9]*",
              "deployment": r"deployments/[1-9][0-9]*/statuses/[1-9][0-9]*"}[source["kind"]]
    require(isinstance(entry["reference"], str)
            and re.fullmatch(re.escape(prefix) + suffix, entry["reference"]),
            f"{gate}: invalid reference")
    fresh(entry["observed_at"], now, rule["max_age_seconds"])
    if rule["scope"] is not None:
        fresh(entry["scope_observed_at"], now, rule["max_age_seconds"])
    else:
        require(entry["scope_observed_at"] is None, "unexpected scope timestamp")
    validate_entry_scope(entry, rule, lifecycle, revision_sha, prefix)


def validate_entry_scope(entry, rule, lifecycle, revision_sha, prefix):
    """Validate all scope fields, including assertions in optional gates."""
    if rule["scope"] is None:
        require(entry["scope"] is None and entry["scope_reference"] is None,
                "unexpected scope evidence")
        return
    scope = entry["scope"]
    fields = {"gate", "revision", "lifecycle", "required", "scope_rule", "reason"}
    if lifecycle == "archive":
        fields.add("identity")
    exact_fields(scope, fields, "scope")
    require(scope["gate"] == entry["gate"] and scope["revision"] == revision_sha
            and scope["lifecycle"] == lifecycle and scope["required"] is entry["applicable"],
            "scope mismatch")
    require(isinstance(entry["scope_reference"], str)
            and entry["scope_reference"].startswith(prefix + "check-runs/"),
            "scope reference missing")
    if entry["applicable"]:
        require(scope["scope_rule"] is None and scope["reason"] is None, "contradictory scope")
    else:
        require(isinstance(scope["scope_rule"], str)
                and scope["scope_rule"] in rule["scope"]["allowed_rules"]
                and scope["reason"] == rule["scope"]["allowed_rules"][scope["scope_rule"]],
                "scope-backed reason missing")


def validate_manifest(manifest, config, lifecycle, revision_sha, identity, now=None):
    """Structural validation only; archive callers must freshly collect evidence."""
    validate_config(config)
    now = now or datetime.now(UTC)
    exact_fields(manifest, {"schema_version", "repository", "identity", "lifecycle", "revision",
                           "trusted_base_revision", "config_sha256", "generated_at", "gates",
                           "archive_context"},
                 "manifest")
    require(type(manifest["schema_version"]) is int
            and manifest["schema_version"] == SCHEMA_VERSION, "unsupported manifest schema")
    require(manifest["repository"] == config["repository"]
            and manifest["identity"] == identity and manifest["lifecycle"] == lifecycle
            and manifest["revision"] == revision_sha, "manifest identity/revision mismatch")
    revision(manifest["trusted_base_revision"])
    require(manifest["config_sha256"] == config_digest(config), "configuration mismatch")
    fresh(manifest["generated_at"], now, config["manifest_max_age_seconds"])
    entries = manifest["gates"]
    require(isinstance(entries, list) and all(isinstance(entry, dict) for entry in entries),
            "malformed gates")
    names = [entry.get("gate") for entry in entries]
    require(all(isinstance(name, str) for name in names), "malformed gate name")
    require(len(names) == len(set(names)) and set(names) == required_gates(lifecycle),
            "missing, duplicate, or unknown gates")
    validate_gate_entries(manifest, config, lifecycle, revision_sha, now)
    validate_archive_manifest(manifest)
    validate_manifest_mapping(manifest, config, now)


def validate_gate_entries(manifest, config, lifecycle, revision_sha, now):
    """Validate context before indexing optional cross-repository gate revisions."""
    if lifecycle == "archive":
        exact_fields(manifest["archive_context"], ARCHIVE_CONTEXT_FIELDS, "archive context")
    for entry in manifest["gates"]:
        operational = lifecycle == "archive" and entry["gate"] in ARCHIVE_GATES
        context = manifest["archive_context"] if operational else {}
        validate_entry(entry, config, lifecycle,
                       context["deployed_revision"] if operational else revision_sha, now,
                       context["deployed_repository"] if operational else config["repository"])


def validate_archive_manifest(manifest):
    """Require explicit store, PR and release/deployment bindings at archive."""
    context = manifest["archive_context"]
    if manifest["lifecycle"] != "archive":
        require(context is None, "unexpected archive context")
        return
    exact_fields(context, ARCHIVE_CONTEXT_FIELDS, "archive context")
    require(isinstance(context["store"], str) and context["store"].strip()
            and isinstance(context["change"], str) and context["change"].strip(),
            "archive store/change required")
    require(manifest["identity"] == f"change:{context['store']}:{context['change']}",
            "archive store/change identity mismatch")
    require(type(context["pr"]) is int and context["pr"] > 0, "archive PR required")
    revision(context["deployed_revision"])
    require(all(entry["scope"] is None or entry["scope"].get("identity") == manifest["identity"]
                for entry in manifest["gates"]), "archive scope identity mismatch")
    needs_release = any(entry["applicable"] for entry in manifest["gates"]
                        if entry["gate"] in {"deployment", "release_readiness"})
    if needs_release or context["release_id"] is not None:
        require(type(context["release_id"]) is int and context["release_id"] > 0,
                "published release required")
        require(context["release_revision"] == context["deployed_revision"], "release revision mismatch")
        require(context["release_reference"] == f"https://api.github.com/repos/"
                f"{context['deployed_repository']}/releases/{context['release_id']}",
                "release reference mismatch")
    else:
        require(context["release_revision"] is None and context["release_reference"] is None,
                "unexpected release claim")


def validate_manifest_mapping(manifest, config, now):
    """Structural authorization cannot substitute for the collector's link rechecks."""
    from fabric_mapping import authorize_pair

    if manifest["lifecycle"] != "archive":
        return
    context = manifest["archive_context"]
    authorize_pair(config["mapping"], manifest["repository"], context["deployed_repository"])
    mapping = context["mapping"]
    if context["deployed_revision"] == manifest["revision"]:
        require(mapping is None, "same-SHA path cannot substitute a mapping claim")
        return
    policy = config["mapping"]
    require(policy is not None, "different revisions need mapping policy")
    exact_fields(mapping, {"source", "reference", "observed_at", "expires_at", "record_sha256", "completed_at"},
                 "mapping result")
    require(mapping["source"] == policy["source"], "unauthorized mapping result source")
    prefix = f"https://api.github.com/repos/{manifest['repository']}/check-runs/"
    require(isinstance(mapping["reference"], str)
            and re.fullmatch(re.escape(prefix) + r"[1-9][0-9]*", mapping["reference"]),
            "invalid mapping result reference")
    fresh(mapping["observed_at"], now, policy["max_age_seconds"])
    fresh(mapping["completed_at"], now, policy["max_age_seconds"])
    require(timestamp(mapping["expires_at"]) > now, "mapping result expired")
    require(isinstance(mapping["record_sha256"], str)
            and re.fullmatch(r"[0-9a-f]{64}", mapping["record_sha256"]), "mapping digest required")
    require(context["release_revision"] == context["deployed_revision"]
            and context["release_reference"] is not None, "mapping release link required")
