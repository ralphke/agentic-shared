#!/usr/bin/env python3
"""Opt-in, revision-bound execution traces for Software Fabric changes."""

from __future__ import annotations

import argparse
import hashlib
import html
import io
import json
import os
import re
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Sequence
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

TRACE_VERSION = 1
EVENT_VERSION = 1
POLICY_VERSION = 2
EVIDENCE_VERSION = 1
MAX_EVIDENCE_ARTIFACT_BYTES = 10 * 1024 * 1024
MAX_EVIDENCE_ARTIFACT_ENTRIES = 100
MAX_EVIDENCE_MEMBER_BYTES = 1024 * 1024
STAGES = (
    "proposal",
    "design",
    "implement",
    "test",
    "security",
    "legal",
    "review",
    "deploy",
    "operate",
)
GATE_STATES = (
    "missing",
    "running",
    "failed",
    "unverified",
    "stale",
    "verified",
    "not-applicable",
)
MANUAL_KINDS = {
    "instruction_discovery",
    "instruction_inclusion",
    "skill_load",
    "agent_invocation",
    "stage_claim",
}
SAFE_METADATA = {
    "assessment",
    "artifact_hashes",
    "coverage",
    "evidence",
    "findings",
    "producer",
    "result",
    "review",
    "run_id",
    "run_attempt",
    "session_reference",
    "source_revision",
    "workflow",
}
UNSAFE_METADATA_KEYS = {
    "args",
    "arguments",
    "argv",
    "authorization",
    "body",
    "command",
    "commands",
    "commandline",
    "commandtext",
    "clientsecret",
    "credential",
    "env",
    "environment",
    "environmentvariables",
    "envvars",
    "processarguments",
    "processoutput",
    "password",
    "passwd",
    "prompt",
    "prompttext",
    "rawarguments",
    "rawcommand",
    "secret",
    "source",
    "sourcebody",
    "standarderror",
    "standardoutput",
    "stdout",
    "stderr",
    "token",
    "apikey",
}
SECRET_PATTERN = re.compile(
    r"(?i)(?:"
    r"\b(?:gh[pousr]_[A-Za-z0-9_]{12,}|github_pat_[A-Za-z0-9_]{12,})\b"
    r"|\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"
    r"|\b(?:password|passwd|secret|token|access[_-]?token|refresh[_-]?token|"
    r"auth[_-]?token|api[_-]?key|client[_-]?secret)\s*[:=]\s*[^\s,;&]+"
    r"|\bbearer\s+[A-Za-z0-9._~+/-]+=*"
    r"|https?://[^/\s:@]+:[^/\s@]+@"
    r")"
)


class TraceError(Exception):
    """An invalid trace, unsafe input, or unavailable evidence source."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def digest_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def safe_text(value: str, field: str = "text", max_length: int = 1000) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TraceError(f"{field} must be a non-empty string")
    if SECRET_PATTERN.search(value):
        raise TraceError(f"{field} appears to contain credential-shaped data")
    if len(value) > max_length:
        raise TraceError(f"{field} exceeds {max_length} characters")
    return value


def sanitize_payload(
    value: Any, *, field: str, reject_credentials: bool, depth: int = 0,
    in_typed_evidence: bool = False,
) -> Any:
    if depth > 8:
        raise TraceError(f"{field} exceeds the maximum nesting depth")
    if isinstance(value, str):
        if len(value) > 4096:
            raise TraceError(f"{field} contains a string exceeding 4096 characters")
        if SECRET_PATTERN.search(value):
            if reject_credentials:
                raise TraceError(f"{field} appears to contain credential-shaped data")
            return SECRET_PATTERN.sub("[REDACTED]", value)
        return value
    if isinstance(value, list):
        return [
            sanitize_payload(item, field=field, reject_credentials=reject_credentials, depth=depth + 1)
            for item in value
        ]
    if isinstance(value, dict):
        sanitized: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise TraceError(f"{field} object keys must be strings")
            normalized_key = re.sub(r"[^a-z0-9]", "", key.lower())
            if normalized_key in UNSAFE_METADATA_KEYS and not (
                in_typed_evidence and normalized_key == "environment"
            ):
                raise TraceError(f"{field} contains unsupported sensitive field: {key}")
            sanitized[key] = sanitize_payload(
                item,
                field=field,
                reject_credentials=reject_credentials,
                depth=depth + 1,
                in_typed_evidence=in_typed_evidence or key == "evidence",
            )
        return sanitized
    if value is None or isinstance(value, (bool, int, float)):
        return value
    raise TraceError(f"{field} contains an unsupported value type")


def safe_url(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TraceError("URL must be a non-empty string")
    if len(value) > 2048:
        raise TraceError("URL exceeds 2048 characters")
    try:
        parsed = urlsplit(value)
        hostname = parsed.hostname
    except ValueError as exc:
        raise TraceError("URL is malformed") from exc
    if (
        parsed.scheme.lower() not in {"http", "https"}
        or not hostname
        or parsed.username
        or parsed.password
        or any(ord(character) < 32 for character in value)
    ):
        raise TraceError("URL must be an http(s) URL without embedded credentials")
    try:
        parsed.port
    except ValueError as exc:
        raise TraceError("URL is malformed") from exc
    query = []
    for key, item in parse_qsl(parsed.query, keep_blank_values=True):
        normalized_key = re.sub(r"[^a-z0-9]", "", key.lower())
        if normalized_key in {
            "password", "passwd", "secret", "token", "accesstoken",
            "refreshtoken", "authtoken", "apikey", "clientsecret",
        } and item:
            item = "[REDACTED]"
        else:
            item = sanitize_payload(item, field="URL", reject_credentials=False)
        query.append((key, item))
    safe_query = urlencode(query, doseq=True, safe="[]")
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, safe_query, parsed.fragment))


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


class FileLock:
    def __init__(self, path: Path, timeout: float = 5.0, stale_after: float = 300.0):
        self.path = path
        self.timeout = timeout
        self.stale_after = stale_after
        self.fd: int | None = None

    def __enter__(self) -> "FileLock":
        deadline = time.monotonic() + self.timeout
        payload = canonical_json({"pid": os.getpid(), "acquiredAt": utc_now()})
        while True:
            try:
                self.fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
                os.write(self.fd, payload)
                os.fsync(self.fd)
                return self
            except FileExistsError:
                try:
                    age = time.time() - self.path.stat().st_mtime
                except FileNotFoundError:
                    continue
                if age > self.stale_after:
                    raise TraceError(
                        f"stale lock at {self.path}; verify no writer is active, then remove it manually"
                    )
                if time.monotonic() >= deadline:
                    raise TraceError(f"conflicting writer holds lock {self.path}")
                time.sleep(0.05)

    def __exit__(self, *_: object) -> None:
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None
            try:
                self.path.unlink()
            except FileNotFoundError:
                pass


def run_git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode:
        detail = result.stderr.strip() or f"git exited {result.returncode}"
        raise TraceError(detail)
    return result.stdout.strip()


def discover_change_paths(repo: Path, slug: str) -> list[Path]:
    matches: list[Path] = []
    for root in (repo / "openspec" / "changes", repo / "spec" / "openspec" / "changes"):
        candidate = root / slug
        if candidate.is_dir():
            matches.append(candidate.resolve())
    return matches


def resolve_change_dir(repo: Path, raw: str) -> Path:
    if not raw or Path(raw).name == raw and ("/" not in raw and "\\" not in raw):
        matches = discover_change_paths(repo, raw)
        if len(matches) > 1:
            raise TraceError(
                "ambiguous change slug; provide an explicit --change-dir path: "
                + ", ".join(str(item) for item in matches)
            )
        if matches:
            raise TraceError(
                f"--change-dir must be an explicit path, not a slug; use {matches[0]}"
            )
        raise TraceError(f"change directory does not exist: {raw}")
    change_dir = Path(raw).expanduser()
    if not change_dir.is_absolute():
        change_dir = repo / change_dir
    change_dir = change_dir.resolve(strict=True)
    if not change_dir.is_dir():
        raise TraceError(f"change directory is not a directory: {change_dir}")
    try:
        change_dir.relative_to(repo.resolve())
    except ValueError as exc:
        raise TraceError("change directory must be inside the repository") from exc
    return change_dir


def repository_identity(repo: Path) -> dict[str, str]:
    root = Path(run_git(repo, "rev-parse", "--show-toplevel")).resolve()
    remotes = run_git(root, "remote", "-v")
    origin = ""
    for line in remotes.splitlines():
        fields = line.split()
        if len(fields) >= 2 and fields[0] == "origin" and (len(fields) == 2 or fields[2] == "(fetch)"):
            origin = fields[1]
            break
    return {"root": str(root), "origin": origin or str(root)}


def resolve_repo(raw: str | None) -> Path:
    start = Path(raw).expanduser().resolve() if raw else Path.cwd().resolve()
    root = Path(run_git(start, "rev-parse", "--show-toplevel")).resolve()
    return root


def trace_paths(trace_dir: Path) -> dict[str, Path]:
    resolved = trace_dir.resolve()
    return {
        "root": resolved,
        "metadata": resolved / "trace.json",
        "events": resolved / "events.jsonl",
        "evidence": resolved / "evidence",
        "report_json": resolved / "report.json",
        "report_md": resolved / "report.md",
    }


def ensure_contained(root: Path, path: Path, description: str) -> None:
    try:
        path.resolve(strict=False).relative_to(root.resolve())
    except ValueError as exc:
        raise TraceError(f"{description} must remain inside trace directory: {path}") from exc


def validate_trace(metadata: Any) -> dict[str, Any]:
    if not isinstance(metadata, dict) or metadata.get("schemaVersion") != TRACE_VERSION:
        raise TraceError(f"unsupported or malformed trace schema version (expected {TRACE_VERSION})")
    try:
        uuid.UUID(metadata["traceId"])
    except (KeyError, ValueError, TypeError) as exc:
        raise TraceError("traceId must be a UUID") from exc
    if not isinstance(metadata.get("repository"), dict) or not metadata["repository"].get("origin"):
        raise TraceError("trace repository identity is missing")
    if not isinstance(metadata.get("changeDir"), str) or not metadata["changeDir"]:
        raise TraceError("trace change directory is missing")
    if not re.fullmatch(r"[0-9a-f]{40,64}", str(metadata.get("targetRevision", ""))):
        raise TraceError("targetRevision must be an immutable Git commit or tree hash")
    if metadata.get("predecessorTraceId") is not None:
        try:
            uuid.UUID(metadata["predecessorTraceId"])
        except (ValueError, TypeError) as exc:
            raise TraceError("predecessorTraceId must be a UUID") from exc
    return metadata


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise TraceError(f"required file is missing: {path}") from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TraceError(f"invalid JSON in {path}: {exc}") from exc


def load_trace(trace_dir: Path) -> tuple[dict[str, Any], dict[str, Path]]:
    paths = trace_paths(trace_dir)
    ensure_contained(paths["root"], paths["metadata"], "trace metadata path")
    metadata = validate_trace(read_json(paths["metadata"]))
    repo = Path(metadata["repository"]["root"]).resolve()
    storage_root = (repo / ".fabric-traces").resolve()
    try:
        storage_root.relative_to(repo)
    except ValueError as exc:
        raise TraceError("trace storage directory must be inside the recorded repository") from exc
    if paths["root"].parent != storage_root or paths["root"].name != metadata["traceId"]:
        raise TraceError(
            "trace directory must be contained by <repository>/.fabric-traces and named <traceId>"
        )
    for key in ("events", "evidence", "report_json", "report_md"):
        ensure_contained(paths["root"], paths[key], f"trace {key} path")
    if not paths["events"].exists():
        raise TraceError(f"event stream is missing: {paths['events']}")
    return metadata, paths


def validate_event(event: Any, trace: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(event, dict) or event.get("schemaVersion") != EVENT_VERSION:
        raise TraceError(f"unsupported or malformed event schema version (expected {EVENT_VERSION})")
    if event.get("traceId") != trace["traceId"]:
        raise TraceError("event belongs to a different trace")
    if event.get("stage") not in STAGES:
        raise TraceError("event has an unknown stage")
    if event.get("targetRevision") != trace["targetRevision"]:
        raise TraceError("event target revision does not match the immutable trace revision")
    try:
        uuid.UUID(event["eventId"])
        if event.get("invocationId") is not None:
            uuid.UUID(event["invocationId"])
    except (KeyError, ValueError, TypeError) as exc:
        raise TraceError("eventId and invocationId must be UUIDs") from exc
    if event.get("provenance") not in {"collector-observed", "provider-verified", "self-reported"}:
        raise TraceError("event has an invalid provenance classification")
    if not isinstance(event.get("summary"), str):
        raise TraceError("event summary must be a string")
    safe_text(event["summary"], "summary")
    if "metadata" in event:
        if not isinstance(event["metadata"], dict):
            raise TraceError("event metadata must be an object")
        if "evidence" in event["metadata"]:
            validate_evidence(event["metadata"]["evidence"], stage=event["stage"])
        sanitize_payload(event["metadata"], field="event metadata", reject_credentials=True)
    if "references" in event:
        if not isinstance(event["references"], list):
            raise TraceError("event references must be a list")
        for reference in event["references"]:
            if not isinstance(reference, dict) or not isinstance(reference.get("value"), str):
                raise TraceError("event references must contain string values")
            if reference.get("type") == "url":
                if safe_url(reference["value"]) != reference["value"]:
                    raise TraceError("event URL contains credential-shaped data")
                reference_fields = {key: value for key, value in reference.items() if key != "value"}
                sanitize_payload(reference_fields, field="event reference", reject_credentials=True)
            else:
                sanitize_payload(reference, field="event reference", reject_credentials=True)
    return event


def read_events(trace: dict[str, Any], path: Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError as exc:
        raise TraceError(f"event stream is missing: {path}") from exc
    for number, line in enumerate(lines, 1):
        if not line.strip():
            raise TraceError(f"malformed event stream: blank line at {number}")
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            suffix = " (possibly truncated)" if number == len(lines) else ""
            raise TraceError(f"malformed event stream at line {number}{suffix}: {exc}") from exc
        try:
            events.append(validate_event(event, trace))
        except TraceError as exc:
            raise TraceError(f"invalid event at line {number}: {exc}") from exc
    return events


def append_event(
    trace: dict[str, Any], paths: dict[str, Path], *, kind: str, stage: str,
    summary: str, provenance: str, invocation_id: str | None = None,
    status: str | None = None, metadata: dict[str, Any] | None = None,
    references: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    event = {
        "schemaVersion": EVENT_VERSION,
        "eventId": str(uuid.uuid4()),
        "traceId": trace["traceId"],
        "timestamp": utc_now(),
        "kind": kind,
        "stage": stage,
        "provenance": provenance,
        "summary": safe_text(
            sanitize_payload(summary, field="summary", reject_credentials=False),
            "summary",
        ),
        "targetRevision": trace["targetRevision"],
    }
    if invocation_id:
        event["invocationId"] = invocation_id
    if status:
        event["status"] = status
    if metadata is not None:
        if "evidence" in metadata:
            validate_evidence(metadata["evidence"], stage=stage)
        event["metadata"] = sanitize_payload(
            metadata, field="metadata", reject_credentials=False
        )
    if references is not None:
        event["references"] = []
        for reference in references:
            if isinstance(reference, dict) and reference.get("type") == "url":
                sanitized_reference = {
                    key: (
                        safe_url(value)
                        if key == "value"
                        else sanitize_payload(value, field="references", reject_credentials=False)
                    )
                    for key, value in reference.items()
                }
                event["references"].append(sanitized_reference)
            else:
                event["references"].append(
                    sanitize_payload(reference, field="references", reject_credentials=False)
                )
    validate_event(event, trace)
    with FileLock(paths["events"].with_suffix(".jsonl.lock")):
        read_events(trace, paths["events"])
        with paths["events"].open("ab") as stream:
            stream.write(canonical_json(event) + b"\n")
            stream.flush()
            os.fsync(stream.fileno())
    return event


STAGE_EVIDENCE_TYPES = {
    "proposal": {"planning-approval"},
    "design": {"planning-approval"},
    "implement": {"implementation-validation"},
    "test": {"test-results"},
    "security": {"security-findings"},
    "legal": {"legal-assessment"},
    "review": {"review-approval"},
    "deploy": {"deployment-lineage"},
    "operate": {"operations-observation"},
}
PRODUCER_TYPES = {"github-actions", "github-review", "github-deployment", "local-collector"}
POLICY_FIELDS = {"schemaVersion", "evidenceVersion", "stages"}
CONTRACT_FIELDS = {
    "requiredEvidence", "trustedProducers", "requiredScanners", "requiredApprovers",
    "allowNotApplicable",
}
EVIDENCE_FIELDS = {
    "planning-approval": {"artifactHashes", "sourceRevision", "approval"},
    "implementation-validation": {"sourceRevision", "treeHash", "validationStatus", "taskSummary", "checks"},
    "test-results": {"sourceRevision", "producerRun", "tests", "coveragePercent"},
    "security-findings": {"sourceRevision", "producerRun", "scanners", "findings"},
    "legal-assessment": {"sourceRevision", "riskLevel", "triggers", "assessment", "assessor"},
    "review-approval": {"sourceRevision", "reviewer", "decision", "reference"},
    "deployment-lineage": {
        "environment", "artifactId", "sourceRevision", "deployedRevision",
        "lineageVerified", "result",
    },
    "operations-observation": {
        "environment", "artifactId", "sourceRevision", "observedAt",
        "observationStatus", "sloConfigured",
    },
}


def require_object(
    value: Any, field: str, required: set[str], optional: set[str] | None = None
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TraceError(f"{field} must be an object")
    if not all(isinstance(key, str) for key in value):
        raise TraceError(f"{field} keys must be strings")
    allowed = required | (optional or set())
    missing = required - set(value)
    unknown = set(value) - allowed
    if missing:
        raise TraceError(f"{field} is missing required fields: {', '.join(sorted(missing))}")
    if unknown:
        raise TraceError(f"{field} contains unsupported fields: {', '.join(sorted(unknown))}")
    return value


def require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TraceError(f"{field} must be a non-empty string")
    safe_text(value, field)
    return value


def require_choice(value: Any, choices: set[str], field: str) -> str:
    if not isinstance(value, str) or value not in choices:
        raise TraceError(f"{field} must be one of: {', '.join(sorted(choices))}")
    return value


def require_revision(value: Any, field: str) -> str:
    value = require_text(value, field)
    if not re.fullmatch(r"[0-9a-f]{40,64}", value):
        raise TraceError(f"{field} must be a lowercase Git revision")
    return value


def require_string_list(value: Any, field: str, *, allow_empty: bool = True) -> list[str]:
    if not isinstance(value, list) or (not allow_empty and not value):
        raise TraceError(f"{field} must be a {'non-empty ' if not allow_empty else ''}list of strings")
    items = [require_text(item, field) for item in value]
    if len(items) != len(set(items)):
        raise TraceError(f"{field} must not contain duplicates")
    return items


def validate_reference(value: Any, field: str) -> dict[str, str]:
    reference = require_object(value, field, {"type", "value"})
    if reference["type"] != "url":
        raise TraceError(f"{field}.type must be 'url'")
    url = require_text(reference["value"], f"{field}.value")
    if safe_url(url) != url:
        raise TraceError(f"{field}.value contains credential-shaped data")
    return reference


def validate_actor_reference(value: Any, field: str) -> dict[str, Any]:
    actor = require_object(value, field, {"actor", "reference"})
    require_text(actor["actor"], f"{field}.actor")
    validate_reference(actor["reference"], f"{field}.reference")
    return actor


def validate_archive_member_path(value: Any, field: str) -> str:
    path = require_text(value, field)
    parts = path.split("/")
    if (
        path.startswith("/")
        or "\\" in path
        or re.match(r"^[A-Za-z]:", path)
        or any(part in {"", ".", ".."} for part in parts)
        or str(PurePosixPath(path)) != path
    ):
        raise TraceError(f"{field} must be a safe relative ZIP member path")
    return path


def validate_producer(producer: Any, stage: str) -> dict[str, Any]:
    producer = require_object(
        producer,
        f"policy trusted producer for {stage}",
        {"id", "type", "repository"},
        {
            "workflow", "requiredJobs", "requiredSteps", "approvers",
            "environment", "evidenceArtifacts",
        },
    )
    require_text(producer["id"], f"policy trusted producer for {stage}.id")
    producer_type = producer["type"]
    if not isinstance(producer_type, str) or producer_type not in PRODUCER_TYPES:
        raise TraceError(f"policy trusted producer for {stage} has an unsupported type")
    repository = require_text(producer["repository"], f"policy trusted producer for {stage}.repository")
    if producer_type == "local-collector":
        if repository != "local":
            raise TraceError(f"local-collector repository for {stage} must be 'local'")
    elif not re.fullmatch(r"[^/\s]+/[^/\s]+", repository):
        raise TraceError(f"policy trusted producer for {stage}.repository must be OWNER/REPOSITORY")
    if producer_type == "github-actions":
        workflow = require_text(producer.get("workflow"), f"policy trusted producer for {stage}.workflow")
        if workflow.startswith("/") or ".." in PurePosixPath(workflow).parts:
            raise TraceError(f"policy trusted producer workflow for {stage} must be repository-relative")
    for key in ("requiredJobs", "requiredSteps", "approvers"):
        if key in producer:
            require_string_list(producer[key], f"policy trusted producer for {stage}.{key}")
    if "environment" in producer:
        require_text(producer["environment"], f"policy trusted producer for {stage}.environment")
    if "evidenceArtifacts" in producer:
        if producer_type != "github-actions":
            raise TraceError(f"evidenceArtifacts for {stage} require a github-actions producer")
        artifacts = producer["evidenceArtifacts"]
        if not isinstance(artifacts, list) or not artifacts:
            raise TraceError(f"policy evidenceArtifacts for {stage} must be a non-empty list")
        selections: set[tuple[str, str]] = set()
        for index, selection in enumerate(artifacts):
            field = f"policy evidenceArtifacts for {stage}[{index}]"
            selection = require_object(
                selection, field, {"artifactName", "archivePath", "evidenceType"}
            )
            artifact_name = require_text(selection["artifactName"], f"{field}.artifactName")
            member_path = validate_archive_member_path(
                selection["archivePath"], f"{field}.archivePath"
            )
            evidence_type = selection["evidenceType"]
            if (
                not isinstance(evidence_type, str)
                or evidence_type not in STAGE_EVIDENCE_TYPES[stage]
            ):
                raise TraceError(f"{field}.evidenceType is not valid for the {stage} stage")
            if evidence_type not in {"test-results", "security-findings"}:
                raise TraceError(
                    f"{field}.evidenceType must include producer run and attempt provenance"
                )
            if not member_path.lower().endswith(".json"):
                raise TraceError(f"{field}.archivePath must select a JSON member")
            identity = (artifact_name, member_path)
            if identity in selections:
                raise TraceError(f"{field} duplicates an artifactName/archivePath selection")
            selections.add(identity)
    return producer


def validate_evidence(evidence: Any, *, stage: str | None = None) -> dict[str, Any]:
    if (
        not isinstance(evidence, dict)
        or type(evidence.get("schemaVersion")) is not int
        or evidence.get("schemaVersion") != EVIDENCE_VERSION
    ):
        raise TraceError(
            f"unsupported or malformed evidence schema version (expected {EVIDENCE_VERSION})"
        )
    evidence_type = evidence.get("evidenceType")
    if not isinstance(evidence_type, str) or evidence_type not in EVIDENCE_FIELDS:
        raise TraceError("evidence has an unsupported evidenceType")
    if stage is not None and evidence_type not in STAGE_EVIDENCE_TYPES.get(stage, set()):
        raise TraceError(f"{evidence_type} evidence is not valid for the {stage} stage")
    fields = EVIDENCE_FIELDS[evidence_type]
    optional_fields = {"clearance"} if evidence_type == "legal-assessment" else set()
    evidence = require_object(
        evidence,
        f"{evidence_type} evidence",
        {"schemaVersion", "evidenceType"} | fields,
        optional_fields,
    )
    if "sourceRevision" in fields:
        require_revision(evidence["sourceRevision"], f"{evidence_type}.sourceRevision")

    if evidence_type == "planning-approval":
        hashes = evidence["artifactHashes"]
        if not isinstance(hashes, dict) or not hashes:
            raise TraceError("planning-approval.artifactHashes must be a non-empty object")
        for path, digest in hashes.items():
            if (
                not isinstance(path, str)
                or not path
                or any(ord(char) < 32 for char in path)
                or "\\" in path
                or re.match(r"^[A-Za-z]:", path)
                or PurePosixPath(path).is_absolute()
                or ".." in PurePosixPath(path).parts
            ):
                raise TraceError("planning-approval artifact paths must be safe relative paths")
            if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
                raise TraceError(f"planning-approval hash for {path} must be a SHA-256 digest")
        approval = require_object(evidence["approval"], "planning-approval.approval", {"actor", "decision", "reference"})
        require_text(approval["actor"], "planning-approval.approval.actor")
        if approval["decision"] != "approved":
            raise TraceError("planning-approval.approval.decision must be 'approved'")
        validate_reference(approval["reference"], "planning-approval.approval.reference")
    elif evidence_type == "implementation-validation":
        require_revision(evidence["treeHash"], "implementation-validation.treeHash")
        require_choice(evidence["validationStatus"], {"passed", "failed"}, "implementation-validation.validationStatus")
        require_text(evidence["taskSummary"], "implementation-validation.taskSummary")
        checks = evidence["checks"]
        if not isinstance(checks, list):
            raise TraceError("implementation-validation.checks must be a list")
        for check in checks:
            check = require_object(check, "implementation-validation check", {"name", "status"})
            require_text(check["name"], "implementation-validation check.name")
            require_choice(check["status"], {"passed", "failed", "skipped"}, "implementation-validation check.status")
    elif evidence_type in {"test-results", "security-findings"}:
        run = require_object(evidence["producerRun"], f"{evidence_type}.producerRun", {"runId", "attempt"})
        require_text(run["runId"], f"{evidence_type}.producerRun.runId")
        if type(run["attempt"]) is not int or run["attempt"] < 1:
            raise TraceError(f"{evidence_type}.producerRun.attempt must be a positive integer")
        if evidence_type == "test-results":
            tests = require_object(evidence["tests"], "test-results.tests", {"total", "passed", "failed", "errors"})
            counts = {}
            for name, count in tests.items():
                if type(count) is not int or count < 0:
                    raise TraceError(f"test-results.tests.{name} must be a non-negative integer")
                counts[name] = count
            if counts["passed"] + counts["failed"] + counts["errors"] > counts["total"]:
                raise TraceError("test-results counts cannot exceed the total")
            coverage = evidence["coveragePercent"]
            if isinstance(coverage, bool) or not isinstance(coverage, (int, float)) or not 0 <= coverage <= 100:
                raise TraceError("test-results.coveragePercent must be a number from 0 to 100")
        else:
            require_string_list(evidence["scanners"], "security-findings.scanners")
            findings = require_object(
                evidence["findings"], "security-findings.findings",
                {"critical", "high", "medium", "low"},
            )
            for severity, count in findings.items():
                if type(count) is not int or count < 0:
                    raise TraceError(f"security-findings.findings.{severity} must be a non-negative integer")
    elif evidence_type == "legal-assessment":
        require_choice(evidence["riskLevel"], {"low", "high"}, "legal-assessment.riskLevel")
        require_string_list(evidence["triggers"], "legal-assessment.triggers")
        require_text(evidence["assessment"], "legal-assessment.assessment")
        validate_actor_reference(evidence["assessor"], "legal-assessment.assessor")
        if "clearance" in evidence:
            clearance = require_object(evidence["clearance"], "legal-assessment.clearance", {"actor", "decision", "reference"})
            require_text(clearance["actor"], "legal-assessment.clearance.actor")
            if clearance["decision"] != "approved":
                raise TraceError("legal-assessment.clearance.decision must be 'approved'")
            validate_reference(clearance["reference"], "legal-assessment.clearance.reference")
    elif evidence_type == "review-approval":
        validate_actor_reference(
            {"actor": evidence["reviewer"], "reference": evidence["reference"]},
            "review-approval.reviewer",
        )
        require_choice(evidence["decision"], {"approved", "changes_requested"}, "review-approval.decision")
    elif evidence_type == "deployment-lineage":
        require_text(evidence["environment"], "deployment-lineage.environment")
        require_text(evidence["artifactId"], "deployment-lineage.artifactId")
        require_revision(evidence["sourceRevision"], "deployment-lineage.sourceRevision")
        require_revision(evidence["deployedRevision"], "deployment-lineage.deployedRevision")
        if type(evidence["lineageVerified"]) is not bool:
            raise TraceError("deployment-lineage.lineageVerified must be a boolean")
        require_choice(evidence["result"], {"succeeded", "failed"}, "deployment-lineage.result")
    elif evidence_type == "operations-observation":
        require_text(evidence["environment"], "operations-observation.environment")
        require_text(evidence["artifactId"], "operations-observation.artifactId")
        if type(evidence["sloConfigured"]) is not bool:
            raise TraceError("operations-observation.sloConfigured must be a boolean")
        require_choice(evidence["observationStatus"], {"succeeded", "failed"}, "operations-observation.observationStatus")
        observed_at = require_text(evidence["observedAt"], "operations-observation.observedAt")
        try:
            parsed_observed_at = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
        except ValueError as exc:
            raise TraceError("operations-observation.observedAt must be an ISO 8601 timestamp") from exc
        if parsed_observed_at.tzinfo is None:
            raise TraceError("operations-observation.observedAt must include a timezone")
    return evidence


def validate_policy(policy: Any) -> dict[str, Any]:
    if (
        not isinstance(policy, dict)
        or type(policy.get("schemaVersion")) is not int
        or policy.get("schemaVersion") != POLICY_VERSION
    ):
        raise TraceError(f"unsupported or malformed policy schema version (expected {POLICY_VERSION})")
    policy = require_object(policy, "policy", POLICY_FIELDS)
    if type(policy["evidenceVersion"]) is not int or policy["evidenceVersion"] != EVIDENCE_VERSION:
        raise TraceError(f"unsupported evidence schema version (expected {EVIDENCE_VERSION})")
    stages = policy["stages"]
    if not isinstance(stages, dict) or set(stages) != set(STAGES):
        raise TraceError("policy must define exactly the nine required stages")
    for stage, contract in stages.items():
        contract = require_object(contract, f"policy contract for {stage}", {"requiredEvidence", "trustedProducers"}, CONTRACT_FIELDS)
        required = require_string_list(contract["requiredEvidence"], f"policy requiredEvidence for {stage}", allow_empty=False)
        unsupported = set(required) - STAGE_EVIDENCE_TYPES[stage]
        if unsupported:
            raise TraceError(f"policy requiredEvidence for {stage} has unsupported types: {', '.join(sorted(unsupported))}")
        producers = contract["trustedProducers"]
        if not isinstance(producers, list):
            raise TraceError(f"policy trustedProducers for {stage} must be a list")
        producer_ids: set[str] = set()
        for producer in producers:
            validated = validate_producer(producer, stage)
            if validated["id"] in producer_ids:
                raise TraceError(f"policy trusted producer IDs for {stage} must be unique")
            producer_ids.add(validated["id"])
        if "requiredScanners" in contract:
            if stage != "security":
                raise TraceError("requiredScanners is only valid for the security stage")
            require_string_list(contract["requiredScanners"], f"policy requiredScanners for {stage}")
        if "requiredApprovers" in contract:
            if stage not in {"proposal", "design", "legal", "review"}:
                raise TraceError("requiredApprovers is only valid for approval stages")
            require_string_list(contract["requiredApprovers"], f"policy requiredApprovers for {stage}")
        if "allowNotApplicable" in contract:
            if stage != "legal" or type(contract["allowNotApplicable"]) is not bool:
                raise TraceError("allowNotApplicable is a boolean option only for the legal stage")
    return policy


def load_policy(path: Path | None) -> dict[str, Any]:
    if path is None:
        policy = {
            "schemaVersion": POLICY_VERSION,
            "evidenceVersion": EVIDENCE_VERSION,
            "stages": {
                stage: {
                    "requiredEvidence": sorted(STAGE_EVIDENCE_TYPES[stage]),
                    "trustedProducers": [],
                }
                for stage in STAGES
            },
        }
    else:
        policy = read_json(path)
    return validate_policy(policy)


def initialize(args: argparse.Namespace) -> Path:
    repo = resolve_repo(args.repo)
    change_dir = resolve_change_dir(repo, args.change_dir)
    target = run_git(repo, "rev-parse", "HEAD")
    if not re.fullmatch(r"[0-9a-f]{40,64}", target):
        raise TraceError("repository HEAD is not an immutable commit")
    dirty = bool(run_git(repo, "status", "--porcelain"))
    output_root = (repo / args.output_dir).resolve()
    try:
        output_root.relative_to(repo.resolve())
    except ValueError as exc:
        raise TraceError("trace output directory must be inside the repository") from exc
    expected_output_root = (repo / ".fabric-traces").resolve()
    if output_root != expected_output_root:
        raise TraceError("trace output directory must be <repository>/.fabric-traces")
    policy = load_policy(Path(args.policy).resolve() if args.policy else None)
    trace_id = str(uuid.uuid4())
    trace_dir = output_root / trace_id
    trace_dir.mkdir(parents=True, exist_ok=False)
    policy_bytes = canonical_json(policy) + b"\n"
    atomic_write(trace_dir / "policy.json", policy_bytes)
    metadata = {
        "schemaVersion": TRACE_VERSION,
        "traceId": trace_id,
        "createdAt": utc_now(),
        "repository": repository_identity(repo),
        "changeDir": change_dir.relative_to(repo).as_posix(),
        "targetRevision": target,
        "dirtyAtInitialization": dirty,
        "policyDigest": hashlib.sha256(canonical_json(policy)).hexdigest(),
        "predecessorTraceId": args.predecessor,
        "simulation": bool(args.simulation),
        "references": {},
    }
    validate_trace(metadata)
    atomic_write(trace_dir / "trace.json", canonical_json(metadata) + b"\n")
    atomic_write(trace_dir / "events.jsonl", b"")
    print(trace_dir)
    return trace_dir


def command_record(args: argparse.Namespace) -> int:
    trace, paths = load_trace(Path(args.trace_dir))
    if args.kind not in MANUAL_KINDS:
        raise TraceError(f"manual record kind must be one of: {', '.join(sorted(MANUAL_KINDS))}")
    metadata: dict[str, Any] = {}
    if args.metadata_json:
        raw = json.loads(args.metadata_json)
        if not isinstance(raw, dict):
            raise TraceError("metadata must be a JSON object")
        unknown = set(raw) - SAFE_METADATA
        if unknown:
            raise TraceError(f"unsupported metadata fields: {', '.join(sorted(unknown))}")
        metadata = sanitize_payload(raw, field="metadata", reject_credentials=True)
    references: list[dict[str, str]] = []
    if args.session_ref:
        references.append({"type": "self-reported-session", "value": safe_text(args.session_ref, "session reference", 256)})
    if args.url:
        references.append({"type": "url", "value": safe_url(args.url)})
    event = append_event(
        trace, paths, kind=args.kind, stage=args.stage, summary=args.summary,
        provenance="self-reported", metadata=metadata or None,
        references=references or None,
    )
    print(event["eventId"])
    return 0


def workspace_state(repo: Path) -> tuple[str, bool]:
    return run_git(repo, "rev-parse", "HEAD"), bool(run_git(repo, "status", "--porcelain"))


def command_run(args: argparse.Namespace) -> int:
    trace, paths = load_trace(Path(args.trace_dir))
    repo = Path(trace["repository"]["root"]).resolve()
    command = args.command[1:] if args.command and args.command[0] == "--" else args.command
    if not command:
        raise TraceError("provide a command after --")
    if any(SECRET_PATTERN.search(arg) for arg in command):
        raise TraceError("command arguments appear to contain credential-shaped data")
    before_revision, before_dirty = workspace_state(repo)
    invocation_id = str(uuid.uuid4())
    summary = safe_text(args.summary or Path(command[0]).name, "summary")
    append_event(
        trace, paths, kind="command_started", stage=args.stage, summary=summary,
        provenance="collector-observed", invocation_id=invocation_id, status="running",
        metadata={"workspaceRevision": before_revision, "workspaceDirty": before_dirty},
    )
    exit_code = 127
    completion_status = "launch-failed"
    try:
        result = subprocess.run(command, cwd=repo, check=False)
        exit_code = result.returncode
        completion_status = "succeeded" if exit_code == 0 else "failed"
    except KeyboardInterrupt:
        completion_status = "interrupted"
        exit_code = 130
        print("command interrupted", file=sys.stderr)
    except OSError as exc:
        completion_status = "launch-failed"
        print(f"could not launch command: {exc}", file=sys.stderr)
    after_revision, after_dirty = workspace_state(repo)
    append_event(
        trace, paths, kind="command_completed", stage=args.stage,
        summary=f"{summary} ({completion_status})", provenance="collector-observed",
        invocation_id=invocation_id, status=completion_status,
        metadata={
            "exitCode": exit_code,
            "startedRevision": before_revision,
            "completedRevision": after_revision,
            "workspaceDirtyAtStart": before_dirty,
            "workspaceDirtyAtCompletion": after_dirty,
            "targetMatches": before_revision == trace["targetRevision"] == after_revision,
        },
    )
    return exit_code


def escape_markdown(value: Any) -> str:
    text = html.escape(str(value), quote=False)
    return re.sub(r"([\\`*_{}\[\]()#+.!|>~-])", r"\\\1", text)


def policy_for(trace_dir: Path) -> dict[str, Any]:
    return load_policy(trace_dir / "policy.json")


def evidence_failure(evidence: dict[str, Any], contract: dict[str, Any]) -> str | None:
    evidence_type = evidence["evidenceType"]
    if evidence_type == "implementation-validation":
        if evidence["validationStatus"] != "passed":
            return "implementation validation did not pass"
        if any(check["status"] != "passed" for check in evidence["checks"]):
            return "implementation validation contains a failed or skipped check"
    elif evidence_type == "test-results":
        if evidence["tests"]["total"] == 0:
            return "test results contain no tests"
        if evidence["tests"]["failed"] or evidence["tests"]["errors"]:
            return "test results contain failed tests or errors"
        if evidence["coveragePercent"] < 80:
            return f"test coverage is {evidence['coveragePercent']}%; at least 80% is required"
    elif evidence_type == "security-findings":
        required_scanners = set(contract.get("requiredScanners", []))
        missing_scanners = required_scanners - set(evidence["scanners"])
        if missing_scanners:
            return f"security evidence omits required scanners: {', '.join(sorted(missing_scanners))}"
        findings = evidence["findings"]
        if findings["critical"] or findings["high"]:
            return (
                "security evidence contains "
                f"{findings['critical']} CRITICAL and {findings['high']} HIGH findings"
            )
    elif evidence_type == "legal-assessment":
        if evidence["riskLevel"] == "low":
            if evidence["triggers"]:
                return "low-risk legal assessment lists escalation triggers"
            return None
        if "clearance" not in evidence:
            return "high-risk legal assessment requires explicit clearance"
    elif evidence_type == "review-approval" and evidence["decision"] != "approved":
        return "review decision is not approved"
    elif evidence_type == "deployment-lineage":
        if not evidence["lineageVerified"]:
            return "deployment lineage is not verified"
        if evidence["result"] != "succeeded":
            return "deployment did not succeed"
    elif evidence_type == "operations-observation":
        if evidence["observationStatus"] != "succeeded":
            return "operations observation did not succeed"
        if not evidence["sloConfigured"]:
            return "operations evidence does not confirm configured SLOs"
    return None


def trusted_producer_matches(
    event: dict[str, Any],
    evidence: dict[str, Any],
    producer: dict[str, Any],
    required_approvers: list[str] | None = None,
) -> bool:
    recorded = event.get("metadata", {}).get("producer")
    if not isinstance(recorded, dict):
        return False
    for field in ("id", "type", "repository", "workflow", "environment"):
        recorded_value = (
            recorded.get("deploymentEnvironment")
            if field == "environment"
            else recorded.get(field)
        )
        if field in producer and recorded_value != producer[field]:
            return False
    if event.get("provenance") != "provider-verified":
        if producer["type"] != "local-collector" or event.get("provenance") != "collector-observed":
            return False
    approvers = set(producer.get("requiredApprovers", []))
    approvers.update(required_approvers or [])
    if approvers:
        evidence_type = evidence["evidenceType"]
        actors = []
        if evidence_type == "planning-approval":
            actors.append(evidence["approval"]["actor"])
        elif evidence_type == "legal-assessment":
            actors.append(evidence["assessor"]["actor"])
            if "clearance" in evidence:
                actors.append(evidence["clearance"]["actor"])
        elif evidence_type == "review-approval":
            actors.append(evidence["reviewer"])
        if not approvers.intersection(actors):
            return False
    if evidence["evidenceType"] in {"test-results", "security-findings"}:
        run = evidence["producerRun"]
        if (
            event.get("metadata", {}).get("run_id") != run["runId"]
            or event.get("metadata", {}).get("run_attempt") != run["attempt"]
        ):
            return False
    return True


def effective_evidence_events(
    activity: list[dict[str, Any]], evidence_type: str
) -> list[dict[str, Any]]:
    matching_events = [
        event for event in activity
        if isinstance(event.get("metadata"), dict)
        and isinstance(event["metadata"].get("evidence"), dict)
        and event["metadata"]["evidence"].get("evidenceType") == evidence_type
    ]
    if evidence_type not in {"test-results", "security-findings"}:
        return matching_events[-1:]

    latest_attempts: dict[str, tuple[int, int, dict[str, Any]]] = {}
    for index, event in enumerate(matching_events):
        evidence = event["metadata"]["evidence"]
        producer_run = evidence.get("producerRun", {})
        run_id = producer_run.get("runId")
        attempt = producer_run.get("attempt")
        if not isinstance(run_id, str) or type(attempt) is not int:
            continue
        previous = latest_attempts.get(run_id)
        if previous is None or (attempt, index) > (previous[0], previous[1]):
            latest_attempts[run_id] = (attempt, index, event)
    return [
        item[2]
        for item in sorted(latest_attempts.values(), key=lambda item: item[1])
    ]


def planning_artifacts_match(
    evidence: dict[str, Any], change_dir: Path | None
) -> bool:
    if change_dir is None:
        return True
    root = change_dir.resolve()
    for relative_path, expected_digest in evidence["artifactHashes"].items():
        artifact = (root / PurePosixPath(relative_path)).resolve()
        try:
            artifact.relative_to(root)
            actual_digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
        except (OSError, ValueError):
            return False
        if actual_digest != expected_digest:
            return False
    return True


def local_evidence_is_stale(
    event: dict[str, Any],
    all_events: list[dict[str, Any]] | None,
    dirty_at_initialization: bool,
) -> bool:
    producer = event.get("metadata", {}).get("producer", {})
    if producer.get("type") != "local-collector":
        return False
    if dirty_at_initialization:
        return True
    if all_events is None:
        return False
    event_ids = [item.get("eventId") for item in all_events]
    try:
        evidence_index = event_ids.index(event.get("eventId"))
    except ValueError:
        return False

    latest_command = None
    for index, item in enumerate(all_events):
        if (
            index < evidence_index
            and item.get("stage") == event.get("stage")
            and item.get("kind") == "command_completed"
        ):
            latest_command = item
        if (
            index > evidence_index
            and item.get("stage") == "implement"
            and item.get("kind") == "command_completed"
        ):
            metadata = item.get("metadata", {})
            if metadata.get("workspaceDirtyAtCompletion") or not metadata.get("targetMatches", True):
                return True
    if latest_command is not None:
        metadata = latest_command.get("metadata", {})
        if metadata.get("workspaceDirtyAtCompletion") or not metadata.get("targetMatches", True):
            return True
    return False


def evaluate_stage(
    stage: str,
    activity: list[dict[str, Any]],
    contract: dict[str, Any],
    target_revision: str,
    *,
    all_events: list[dict[str, Any]] | None = None,
    dirty_at_initialization: bool = False,
    change_dir: Path | None = None,
) -> tuple[str, list[str]]:
    reasons: list[str] = []
    statuses: list[str] = []
    legal_not_applicable = False
    for evidence_type in contract["requiredEvidence"]:
        matching_events = effective_evidence_events(activity, evidence_type)
        if not matching_events:
            statuses.append("missing")
            reasons.append(f"missing required typed evidence: {evidence_type}")
            continue

        accepted = False
        type_statuses: list[str] = []
        type_reasons: list[str] = []
        for event in matching_events:
            evidence = event["metadata"]["evidence"]
            producers = [
                producer for producer in contract["trustedProducers"]
                if trusted_producer_matches(
                    event, evidence, producer, contract.get("requiredApprovers")
                )
            ]
            if not producers:
                type_statuses.append("unverified")
                if not contract["trustedProducers"]:
                    type_reasons.append(
                        f"no trusted evidence producer is configured for {evidence_type}"
                    )
                else:
                    type_reasons.append(
                        f"{evidence_type} provenance does not match a trusted producer"
                    )
                continue
            if event.get("status") == "running":
                type_statuses.append("running")
                continue
            if event.get("status") == "failed":
                type_statuses.append("failed")
                type_reasons.append(f"{evidence_type} evidence event failed")
                continue
            if event.get("status") != "verified":
                type_statuses.append("unverified")
                type_reasons.append(f"{evidence_type} evidence is not marked verified")
                continue
            if local_evidence_is_stale(
                event, all_events, dirty_at_initialization
            ):
                type_statuses.append("stale")
                type_reasons.append(
                    f"{evidence_type} was collected from a dirty or subsequently changed workspace"
                )
                continue
            if (
                evidence_type == "planning-approval"
                and not planning_artifacts_match(evidence, change_dir)
            ):
                type_statuses.append("stale")
                type_reasons.append(
                    "planning approval does not match the current artifact hashes"
                )
                continue

            source_revision = evidence.get("sourceRevision")
            if source_revision is not None and source_revision != target_revision:
                type_statuses.append("stale")
                type_reasons.append(f"{evidence_type} is for a different source revision")
                continue
            if (
                evidence_type == "deployment-lineage"
                and evidence["deployedRevision"] != target_revision
                and not evidence["lineageVerified"]
            ):
                type_statuses.append("stale")
                type_reasons.append("deployment is for a different revision")
                continue
            failure = evidence_failure(evidence, contract)
            if failure:
                type_statuses.append("failed")
                type_reasons.append(failure)
                continue
            if evidence_type == "legal-assessment" and evidence["riskLevel"] == "low":
                if contract.get("allowNotApplicable") is True:
                    legal_not_applicable = True
                    accepted = True
                    break
                type_statuses.append("unverified")
                type_reasons.append("policy does not allow low-risk legal review to be not-applicable")
                continue
            accepted = True
        if any(
            status in {"failed", "stale", "unverified", "running"}
            for status in type_statuses
        ):
            accepted = False

        if accepted:
            statuses.append("not-applicable" if legal_not_applicable else "verified")
            continue
        priority = ("failed", "stale", "unverified", "running", "missing")
        status = next((candidate for candidate in priority if candidate in type_statuses), "unverified")
        statuses.append(status)
        reasons.extend(type_reasons or [f"{evidence_type} evidence is {status}"])

    if statuses and all(status == "not-applicable" for status in statuses):
        return "not-applicable", reasons
    if statuses and all(status in {"verified", "not-applicable"} for status in statuses):
        return "not-applicable" if "not-applicable" in statuses else "verified", []
    for status in ("failed", "stale", "unverified", "running", "missing"):
        if status in statuses:
            return status, reasons
    return "missing", reasons or ["stage has no required evidence"]


def stage_evidence_events(
    stage: str,
    events: list[dict[str, Any]],
    policy: dict[str, Any],
) -> list[dict[str, Any]]:
    activity = [event for event in events if event["stage"] == stage]
    selected: list[dict[str, Any]] = []
    for evidence_type in policy["stages"][stage]["requiredEvidence"]:
        selected.extend(effective_evidence_events(activity, evidence_type))
    return selected


def apply_prerequisite_ordering(
    stages: list[dict[str, Any]],
    events: list[dict[str, Any]],
    policy: dict[str, Any],
) -> None:
    stage_by_name = {stage["stage"]: stage for stage in stages}
    event_positions = {event["eventId"]: index for index, event in enumerate(events)}
    positions = {
        stage: [
            event_positions[event["eventId"]]
            for event in stage_evidence_events(stage, events, policy)
            if event.get("eventId") in event_positions
        ]
        for stage in STAGES
    }

    def block(stage: str, reason: str, status: str = "unverified") -> None:
        result = stage_by_name[stage]
        if result["gateStatus"] in {"verified", "not-applicable"}:
            result["gateStatus"] = status
            result["reasons"] = [reason]

    for prerequisite in ("proposal", "design"):
        if stage_by_name[prerequisite]["gateStatus"] not in {"verified", "not-applicable"}:
            block("implement", f"blocked by prerequisite {prerequisite} approval")
        elif not positions[prerequisite] or not positions["implement"]:
            block("implement", f"{prerequisite} approval or implementation evidence is missing")
        elif max(positions[prerequisite]) >= min(positions["implement"]):
            block("implement", f"{prerequisite} approval must precede implementation validation")

    if stage_by_name["implement"]["gateStatus"] not in {"verified", "not-applicable"}:
        for stage in ("test", "security", "legal", "review"):
            block(stage, "blocked by prerequisite implementation validation")
    elif positions["implement"]:
        for stage in ("test", "security", "legal", "review"):
            if positions[stage] and min(positions[stage]) <= max(positions["implement"]):
                block(stage, "evidence predates implementation validation")

    deployment = stage_evidence_events("deploy", events, policy)
    deployment_position = max(
        (event_positions[event["eventId"]] for event in deployment if event.get("eventId") in event_positions),
        default=None,
    )
    if deployment_position is not None:
        for prerequisite in ("implement", "test", "security", "legal", "review"):
            if stage_by_name[prerequisite]["gateStatus"] not in {"verified", "not-applicable"}:
                block("deploy", f"blocked by prerequisite {prerequisite} evidence")
            elif not positions[prerequisite] or max(positions[prerequisite]) >= deployment_position:
                block("deploy", f"{prerequisite} evidence must precede deployment")

    observations = stage_evidence_events("operate", events, policy)
    if observations:
        if stage_by_name["deploy"]["gateStatus"] not in {"verified", "not-applicable"}:
            block("operate", "blocked by prerequisite deployment lineage")
        elif deployment_position is None or not positions["operate"] or min(positions["operate"]) <= deployment_position:
            block("operate", "operations observation must follow deployment")
        elif deployment:
            deployed = deployment[-1]["metadata"]["evidence"]
            for observation_event in observations:
                observed = observation_event["metadata"]["evidence"]
                if (
                    observed["environment"] != deployed["environment"]
                    or observed["artifactId"] != deployed["artifactId"]
                ):
                    block("operate", "operations evidence does not match the deployed environment and artifact", "stale")
                    break


def predecessor_history(
    trace: dict[str, Any], repo: Path
) -> list[dict[str, Any]]:
    history: list[dict[str, Any]] = []
    predecessor_id = trace.get("predecessorTraceId")
    seen = {trace["traceId"]}
    while predecessor_id is not None:
        if predecessor_id in seen:
            raise TraceError("predecessor trace chain contains a cycle")
        seen.add(predecessor_id)
        previous_dir = repo / ".fabric-traces" / predecessor_id
        previous, previous_paths = load_trace(previous_dir)
        if (
            previous["repository"] != trace["repository"]
            or previous["changeDir"] != trace["changeDir"]
        ):
            raise TraceError("predecessor trace must belong to the same repository and change directory")
        previous_events = read_events(previous, previous_paths["events"])
        history.append({
            "traceId": previous["traceId"],
            "targetRevision": previous["targetRevision"],
            "createdAt": previous["createdAt"],
            "eventCount": len(previous_events),
            "predecessorTraceId": previous.get("predecessorTraceId"),
        })
        predecessor_id = previous.get("predecessorTraceId")
    return history


def evaluate(trace_dir: Path) -> dict[str, Any]:
    trace, paths = load_trace(trace_dir)
    policy = policy_for(trace_dir)
    if digest_json(policy) != trace.get("policyDigest"):
        raise TraceError("policy digest differs from the immutable trace policy")
    events = read_events(trace, paths["events"])
    stages: list[dict[str, Any]] = []
    for stage in STAGES:
        activity = [event for event in events if event["stage"] == stage]
        contract = policy["stages"][stage]
        started_invocations = {
            event.get("invocationId")
            for event in activity
            if event.get("kind") == "command_started"
            and event.get("status") == "running"
            and event.get("invocationId")
        }
        completed_invocations = {
            event.get("invocationId")
            for event in activity
            if event.get("kind") == "command_completed" and event.get("invocationId")
        }
        has_unfinished_invocation = bool(started_invocations - completed_invocations)
        reasons: list[str] = []
        state, reasons = evaluate_stage(
            stage,
            activity,
            contract,
            trace["targetRevision"],
            all_events=events,
            dirty_at_initialization=trace.get("dirtyAtInitialization") is True,
            change_dir=Path(trace["repository"]["root"]) / PurePosixPath(trace["changeDir"]),
        )
        collection_failed = stage == "test" and any(
            event.get("kind") == "github_collection_error"
            and event.get("status") == "failed"
            for event in activity
        )
        if collection_failed:
            state = "failed"
            reasons = [
                "GitHub evidence collection failed; cached evidence cannot satisfy the test gate"
            ]
        elif state not in {"verified", "not-applicable"} and any(
            event.get("status") == "failed" for event in activity
        ):
            state = "failed"
        elif state not in {"verified", "not-applicable"} and (
            has_unfinished_invocation
            or any(
                event.get("status") == "running"
                and event.get("kind") != "command_started"
                for event in activity
            )
        ):
            state = "running"
        stages.append({
            "stage": stage,
            "activityStatus": "observed" if activity else "not-observed",
            "gateStatus": state,
            "eventIds": [event["eventId"] for event in activity],
            "reasons": reasons,
        })
    apply_prerequisite_ordering(stages, events, policy)
    verified = all(
        stage["gateStatus"] == "verified"
        for stage in stages
        if stage["stage"] != "legal"
    ) and next(stage for stage in stages if stage["stage"] == "legal")["gateStatus"] in {"verified", "not-applicable"}
    return {
        "schemaVersion": TRACE_VERSION,
        "traceId": trace["traceId"],
        "generatedAt": utc_now(),
        "status": "verified-complete" if verified else "incomplete",
        "simulation": trace["simulation"],
        "repository": trace["repository"],
        "changeDir": trace["changeDir"],
        "targetRevision": trace["targetRevision"],
        "policyDigest": trace["policyDigest"],
        "observationBoundary": "Only activity recorded by this local wrapper and configured evidence collectors is observed; other host activity is outside the trace.",
        "predecessorHistory": predecessor_history(
            trace, Path(trace["repository"]["root"])
        ),
        "stages": stages,
        "timeline": events,
        "nextActions": [
            f"{item['stage']}: " + "; ".join(item["reasons"])
            for item in stages if item["gateStatus"] not in {"verified", "not-applicable"}
        ],
    }


def render_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Fabric execution trace",
        "",
        f"- Trace: `{result['traceId']}`",
        f"- Status: **{result['status']}**",
        f"- Simulation: **{'YES — fixture-backed simulation, not a real deployment' if result['simulation'] else 'No'}**",
        f"- Repository: `{escape_markdown(result['repository']['origin'])}`",
        f"- Change directory: `{escape_markdown(result['changeDir'])}`",
        f"- Target revision: `{result['targetRevision']}`",
        f"- Policy digest: `{result['policyDigest']}`",
        "",
        "## Stages",
        "",
        "| Stage | Activity | Gate | Event IDs | Reasons |",
        "|---|---|---|---|---|",
    ]
    for stage in result["stages"]:
        reasons = "; ".join(stage["reasons"]) or "—"
        event_ids = ", ".join(f"`{event_id}`" for event_id in stage["eventIds"]) or "—"
        lines.append(
            f"| {stage['stage']} | {stage['activityStatus']} | {stage['gateStatus']} "
            f"| {event_ids} | {escape_markdown(reasons)} |"
        )
    lines.extend([
        "",
        "## Timeline",
        "",
    ])
    for event in result["timeline"]:
        refs = ", ".join(ref.get("value", "") for ref in event.get("references", []))
        metadata = event.get("metadata", {})
        evidence_ids = ", ".join(
            f"{key}={metadata[key]}"
            for key in (
                "run_id", "run_attempt", "job_id", "step_number",
                "artifact_id", "review_id", "deployment_id",
            )
            if key in metadata
        )
        lines.append(
            f"- `{event['eventId']}` — {event['timestamp']} — "
            f"`{event['stage']}` / `{event['kind']}` "
            f"({event['provenance']}): {escape_markdown(event['summary'])}"
            + (f" — IDs: {escape_markdown(evidence_ids)}" if evidence_ids else "")
            + (f" — {escape_markdown(refs)}" if refs else "")
        )
    lines.extend([
        "",
        "## Predecessor history",
        "",
    ])
    for predecessor in result.get("predecessorHistory", []):
        lines.append(
            f"- `{predecessor['traceId']}` — revision `{predecessor['targetRevision']}`, "
            f"{predecessor['eventCount']} recorded events"
        )
    if not result.get("predecessorHistory"):
        lines.append("No predecessor trace is linked.")
    lines.extend([
        "",
        "## Observation boundary",
        "",
        result["observationBoundary"],
        "",
        "Local trace files are not tamper-proof. Anyone able to modify this workstation's "
        "collector or trace files can alter self-reported or collector-observed data.",
        "",
        "## Next evidence",
        "",
    ])
    lines.extend(f"- {escape_markdown(action)}" for action in result["nextActions"])
    if not result["nextActions"]:
        lines.append("- None.")
    return "\n".join(lines) + "\n"


def command_report(args: argparse.Namespace) -> int:
    trace_dir = Path(args.trace_dir)
    result = evaluate(trace_dir)
    paths = trace_paths(trace_dir)
    atomic_write(paths["report_json"], json.dumps(result, indent=2, ensure_ascii=True).encode("utf-8") + b"\n")
    atomic_write(paths["report_md"], render_markdown(result).encode("utf-8"))
    print(paths["report_md"] if args.format == "markdown" else paths["report_json"])
    return 0


def command_check(args: argparse.Namespace) -> int:
    result = evaluate(Path(args.trace_dir))
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return 0 if result["status"] == "verified-complete" else 1


def gh_api_json(path: str, *, paginate: bool = False) -> list[Any]:
    if not path.startswith("/"):
        raise TraceError("GitHub API path must be absolute")
    command = ["gh", "api", "--method", "GET", "--hostname", "github.com"]
    if paginate:
        command.extend(["--paginate", "--slurp"])
    command.append(path.lstrip("/"))
    result = subprocess.run(command, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
    if result.returncode:
        raise TraceError(f"GitHub evidence collection failed: {result.stderr.strip() or result.returncode}")
    try:
        decoded = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise TraceError(f"GitHub returned malformed JSON: {exc}") from exc
    return decoded if isinstance(decoded, list) else [decoded]


def gh_api_bytes(path: str) -> bytes:
    if not path.startswith("/"):
        raise TraceError("GitHub API path must be absolute")
    with tempfile.TemporaryDirectory(prefix="fabric-trace-artifact-") as temporary_dir:
        output_path = Path(temporary_dir) / "artifact.zip"
        command = [
            "gh", "api", "--method", "GET", "--hostname", "github.com",
            "--output", str(output_path), path.lstrip("/"),
        ]
        result = subprocess.run(
            command, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8",
        )
        if result.returncode:
            raise TraceError(
                f"GitHub artifact download failed: {result.stderr.strip() or result.returncode}"
            )
        if not output_path.is_file():
            raise TraceError("GitHub artifact download did not produce an archive")
        if output_path.stat().st_size > MAX_EVIDENCE_ARTIFACT_BYTES:
            raise TraceError(
                f"GitHub evidence archive exceeds {MAX_EVIDENCE_ARTIFACT_BYTES} bytes"
            )
        return output_path.read_bytes()


def selected_evidence_artifacts(
    policy: dict[str, Any], repository: str, workflow: str,
) -> dict[str, list[tuple[str, dict[str, Any]]]]:
    selected: dict[str, list[tuple[str, dict[str, Any]]]] = {}
    for stage, contract in policy["stages"].items():
        for producer in contract["trustedProducers"]:
            if (
                producer["type"] != "github-actions"
                or producer["repository"].lower() != repository.lower()
                or producer["workflow"] != workflow
            ):
                continue
            for selection in producer.get("evidenceArtifacts", []):
                selected.setdefault(selection["artifactName"], []).append(
                    (stage, {"producer": producer, "selection": selection})
                )
    return selected


def recorded_github_producer(producer: dict[str, Any]) -> dict[str, Any]:
    recorded = dict(producer)
    if "environment" in recorded:
        recorded["deploymentEnvironment"] = recorded.pop("environment")
    return recorded


def parse_evidence_artifact(
    archive_bytes: bytes, member_path: str,
) -> dict[str, Any] | None:
    if len(archive_bytes) > MAX_EVIDENCE_ARTIFACT_BYTES:
        raise TraceError(
            f"GitHub evidence archive exceeds {MAX_EVIDENCE_ARTIFACT_BYTES} bytes"
        )
    try:
        with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
            entries = archive.infolist()
            if len(entries) > MAX_EVIDENCE_ARTIFACT_ENTRIES:
                raise TraceError(
                    f"GitHub evidence archive exceeds {MAX_EVIDENCE_ARTIFACT_ENTRIES} entries"
                )
            names: set[str] = set()
            for entry in entries:
                raw_name = entry.filename[:-1] if entry.is_dir() else entry.filename
                safe_name = validate_archive_member_path(raw_name, "ZIP entry path")
                if safe_name in names:
                    raise TraceError(f"GitHub evidence archive contains duplicate ZIP entry: {safe_name}")
                names.add(safe_name)
                file_mode = (entry.external_attr >> 16) & 0o170000
                if file_mode == stat.S_IFLNK:
                    raise TraceError(f"GitHub evidence archive contains a symbolic link: {safe_name}")
                if entry.flag_bits & 0x1:
                    raise TraceError(f"GitHub evidence archive contains an encrypted entry: {safe_name}")
            matches = [entry for entry in entries if not entry.is_dir() and entry.filename == member_path]
            if not matches:
                return None
            entry = matches[0]
            if entry.file_size > MAX_EVIDENCE_MEMBER_BYTES:
                raise TraceError(
                    f"selected evidence member exceeds {MAX_EVIDENCE_MEMBER_BYTES} bytes"
                )
            with archive.open(entry) as member:
                payload = member.read(MAX_EVIDENCE_MEMBER_BYTES + 1)
            if len(payload) > MAX_EVIDENCE_MEMBER_BYTES:
                raise TraceError(
                    f"selected evidence member exceeds {MAX_EVIDENCE_MEMBER_BYTES} bytes"
                )
            try:
                decoded = json.loads(payload.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise TraceError(f"selected evidence member is not valid UTF-8 JSON: {exc}") from exc
            if not isinstance(decoded, dict):
                raise TraceError("selected evidence member must contain a JSON object")
            return decoded
    except zipfile.BadZipFile as exc:
        raise TraceError(f"GitHub evidence artifact is not a valid ZIP archive: {exc}") from exc
    except (OSError, RuntimeError, ValueError) as exc:
        if isinstance(exc, TraceError):
            raise
        raise TraceError(f"GitHub evidence archive could not be read: {exc}") from exc


def github_api_items(responses: list[Any], collection: str | None = None) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for response in responses:
        if collection is None:
            page_items = response if isinstance(response, list) else [response]
        elif isinstance(response, dict):
            page_items = response.get(collection)
            if not isinstance(page_items, list):
                raise TraceError(f"GitHub response is missing the {collection} collection")
        else:
            raise TraceError(f"GitHub response for {collection} must be an object")
        if not all(isinstance(item, dict) for item in page_items):
            raise TraceError(f"GitHub response contains an invalid {collection or 'record'}")
        items.extend(page_items)
    return items


def github_observation_status(value: Any) -> str:
    if value == "success":
        return "verified"
    if value in {"failure", "timed_out", "action_required", "error"}:
        return "failed"
    return "unverified"


def github_deployment_lineage_verified(
    repository: str, source_revision: str, deployed_revision: str
) -> bool:
    if deployed_revision == source_revision:
        return True
    comparison = gh_api_json(
        f"/repos/{repository}/compare/{source_revision}...{deployed_revision}"
    )
    if len(comparison) != 1 or not isinstance(comparison[0], dict):
        raise TraceError("GitHub returned malformed commit comparison data")
    merge_base = comparison[0].get("merge_base_commit")
    return (
        comparison[0].get("status") == "ahead"
        and isinstance(merge_base, dict)
        and merge_base.get("sha") == source_revision
    )


def github_deployment_producer(
    policy: dict[str, Any], repository: str, environment: str
) -> dict[str, Any]:
    for producer in policy["stages"]["deploy"]["trustedProducers"]:
        if (
            producer["type"] == "github-deployment"
            and producer["repository"].lower() == repository.lower()
            and producer.get("environment", environment) == environment
        ):
            return recorded_github_producer(producer)
    return {
        "id": "unconfigured-github-deployment",
        "type": "github-deployment",
        "repository": repository,
        "deploymentEnvironment": environment,
    }


def effective_reviews(reviews: list[dict[str, Any]]) -> list[dict[str, Any]]:
    latest: dict[str, tuple[str, dict[str, Any]]] = {}
    for review in reviews:
        user = review.get("user") or {}
        reviewer = str(user.get("id") or user.get("login") or "")
        if not reviewer:
            raise TraceError("GitHub review response is missing the reviewer identity")
        submitted_at = review.get("submitted_at") or ""
        if not isinstance(submitted_at, str):
            raise TraceError("GitHub review submitted_at must be a string")
        previous = latest.get(reviewer)
        if previous is None or submitted_at >= previous[0]:
            latest[reviewer] = (submitted_at, review)
    return [entry[1] for entry in latest.values()]


def command_collect_github(args: argparse.Namespace) -> int:
    trace, paths = load_trace(Path(args.trace_dir))
    policy = policy_for(Path(args.trace_dir))
    repo_owner, sep, repo_name = args.repo.partition("/")
    if not sep or not repo_owner or not repo_name:
        raise TraceError("--repo must be OWNER/REPOSITORY")
    try:
        pr_pages = gh_api_json(f"/repos/{repo_owner}/{repo_name}/pulls/{args.pr}")
        pr = pr_pages[0]
        head_repo = (pr.get("head") or {}).get("repo") or {}
        head = (pr.get("head") or {}).get("sha")
        actual_repo = (head_repo.get("full_name") or "").lower()
        expected_repo = f"{repo_owner}/{repo_name}".lower()
        if actual_repo != expected_repo:
            raise TraceError(f"pull request head repository mismatch: {actual_repo}")
        if head != trace["targetRevision"]:
            raise TraceError(f"pull request head revision mismatch: expected {trace['targetRevision']}, got {head}")
        merge_revision_value = pr.get("merge_commit_sha")
        merge_revision = (
            require_revision(merge_revision_value, "pull request merge_commit_sha")
            if merge_revision_value
            else None
        )
        run_pages = gh_api_json(
            f"/repos/{repo_owner}/{repo_name}/actions/runs?head_sha={trace['targetRevision']}",
            paginate=True,
        )
        runs = github_api_items(run_pages, "workflow_runs")
        review_pages = gh_api_json(
            f"/repos/{repo_owner}/{repo_name}/pulls/{args.pr}/reviews",
            paginate=True,
        )
        reviews = github_api_items(review_pages)
        deployment_pages = gh_api_json(
            f"/repos/{repo_owner}/{repo_name}/commits/{trace['targetRevision']}/deployments",
            paginate=True,
        )
        deployments = github_api_items(deployment_pages)
        if merge_revision and merge_revision != trace["targetRevision"]:
            merge_deployment_pages = gh_api_json(
                f"/repos/{repo_owner}/{repo_name}/commits/{merge_revision}/deployments",
                paginate=True,
            )
            known_deployment_ids = {
                str(item.get("id"))
                for item in deployments
                if isinstance(item, dict)
            }
            deployments.extend(
                item for item in github_api_items(merge_deployment_pages)
                if str(item.get("id")) not in known_deployment_ids
            )
        observed = 0
        seen_runs: set[str] = set()
        for run in runs:
            if run.get("head_sha") != trace["targetRevision"]:
                continue
            run_id = str(run.get("id") or "")
            if not run_id or not run_id.isdecimal():
                raise TraceError("GitHub workflow run is missing a valid numeric id")
            if run_id in seen_runs:
                continue
            seen_runs.add(run_id)
            latest_attempt = run.get("run_attempt", 1)
            if type(latest_attempt) is not int or latest_attempt < 1:
                raise TraceError(f"GitHub workflow run {run_id} has an invalid attempt number")
            seen_jobs: set[tuple[int, str]] = set()
            latest_attempt_record: dict[str, Any] | None = None
            for attempt_number in range(1, latest_attempt + 1):
                attempt_responses = gh_api_json(
                    f"/repos/{repo_owner}/{repo_name}/actions/runs/{run_id}/attempts/{attempt_number}"
                )
                attempt = attempt_responses[0] if attempt_responses else None
                if not isinstance(attempt, dict):
                    raise TraceError(f"GitHub run {run_id} attempt {attempt_number} is unavailable")
                if (
                    str(attempt.get("id", run_id)) != run_id
                    or attempt.get("head_sha") != trace["targetRevision"]
                    or attempt.get("run_attempt", attempt_number) != attempt_number
                ):
                    raise TraceError(
                        f"GitHub run {run_id} attempt {attempt_number} does not match the trace revision"
                    )
                if attempt_number == latest_attempt:
                    latest_attempt_record = attempt
                run_url = attempt.get("html_url") or run.get("html_url")
                append_event(
                    trace, paths, kind="github_attempt_observed", stage="test",
                    summary=f"Workflow attempt {attempt_number}: {attempt.get('conclusion') or attempt.get('status', 'unknown')}",
                    provenance="provider-verified",
                    status=github_observation_status(attempt.get("conclusion")),
                    metadata={
                        "run_id": run_id,
                        "run_attempt": attempt_number,
                        "workflow": attempt.get("path", run.get("path", "")),
                        "headSha": attempt.get("head_sha"),
                        "evidenceType": "github-attempt",
                    },
                    references=[{"type": "url", "value": safe_url(run_url)}] if run_url else None,
                )
                observed += 1

                job_pages = gh_api_json(
                    f"/repos/{repo_owner}/{repo_name}/actions/runs/{run_id}/attempts/{attempt_number}/jobs",
                    paginate=True,
                )
                jobs = github_api_items(job_pages, "jobs")
                for job in jobs:
                    job_id = str(job.get("id") or "")
                    if not job_id or not job_id.isdecimal():
                        raise TraceError(f"GitHub run {run_id} attempt {attempt_number} has a job without a valid id")
                    identity = (attempt_number, job_id)
                    if identity in seen_jobs:
                        continue
                    seen_jobs.add(identity)
                    conclusion = job.get("conclusion")
                    append_event(
                        trace, paths, kind="github_job_observed", stage="test",
                        summary=f"{job.get('name', 'unnamed job')} — {conclusion or job.get('status', 'unknown')}",
                        provenance="provider-verified",
                        status=github_observation_status(conclusion),
                        metadata={
                            "run_id": run_id,
                            "run_attempt": attempt_number,
                            "job_id": job_id,
                            "workflow": attempt.get("path", run.get("path", "")),
                            "headSha": attempt.get("head_sha"),
                            "evidenceType": "github-job",
                        },
                        references=[{"type": "url", "value": safe_url(job.get("html_url") or run_url)}]
                        if job.get("html_url") or run_url else None,
                    )
                    observed += 1
                    steps = job.get("steps") or []
                    if not isinstance(steps, list) or not all(isinstance(step, dict) for step in steps):
                        raise TraceError(f"GitHub job {job_id} has an invalid steps collection")
                    for step in steps:
                        conclusion = step.get("conclusion")
                        append_event(
                            trace, paths, kind="github_step_observed", stage="test",
                            summary=f"{job.get('name', 'unnamed job')} / {step.get('name', 'unnamed step')} — {conclusion or step.get('status', 'unknown')}",
                            provenance="provider-verified",
                            status=github_observation_status(conclusion),
                            metadata={
                                "run_id": run_id,
                                "run_attempt": attempt_number,
                                "job_id": job_id,
                                "step_number": step.get("number"),
                                "step_name": step.get("name", ""),
                                "workflow": attempt.get("path", run.get("path", "")),
                                "headSha": attempt.get("head_sha"),
                                "evidenceType": "github-step",
                            },
                            references=[{"type": "url", "value": safe_url(job.get("html_url") or run_url)}]
                            if job.get("html_url") or run_url else None,
                        )
                        observed += 1

            artifact_pages = gh_api_json(
                f"/repos/{repo_owner}/{repo_name}/actions/runs/{run_id}/artifacts",
                paginate=True,
            )
            artifacts = github_api_items(artifact_pages, "artifacts")
            workflow = (
                latest_attempt_record.get("path", run.get("path", ""))
                if latest_attempt_record is not None else run.get("path", "")
            )
            selected = selected_evidence_artifacts(policy, expected_repo, workflow)
            for artifact in artifacts:
                artifact_id = str(artifact.get("id") or "")
                if not artifact_id or not artifact_id.isdecimal():
                    raise TraceError(f"GitHub run {run_id} has an artifact without a valid id")
                artifact_url = artifact.get("url")
                append_event(
                    trace, paths, kind="github_artifact_observed", stage="test",
                    summary=f"Artifact metadata: {artifact.get('name', 'unnamed artifact')}",
                    provenance="provider-verified",
                    status="unverified" if artifact.get("expired") else "verified",
                    metadata={
                        "run_id": run_id,
                        "artifact_id": artifact_id,
                        "name": artifact.get("name", ""),
                        "sizeInBytes": artifact.get("size_in_bytes"),
                        "expired": bool(artifact.get("expired", False)),
                        "evidenceType": "github-artifact-metadata",
                    },
                    references=[{"type": "url", "value": safe_url(artifact_url)}] if artifact_url else None,
                )
                observed += 1
            if selected:
                artifacts_by_name: dict[str, list[dict[str, Any]]] = {}
                for artifact in artifacts:
                    name = artifact.get("name")
                    if isinstance(name, str):
                        artifacts_by_name.setdefault(name, []).append(artifact)
                for artifact_name, selections in selected.items():
                    matches = artifacts_by_name.get(artifact_name, [])
                    for stage, selection_data in selections:
                        producer = selection_data["producer"]
                        selection = selection_data["selection"]
                        evidence_metadata = {
                            "run_id": run_id,
                            "run_attempt": latest_attempt,
                            "workflow": workflow,
                            "artifactName": artifact_name,
                            "evidenceType": selection["evidenceType"],
                            "producer": recorded_github_producer(producer),
                        }
                        reject_reason = None
                        reject_status = "unverified"
                        if (
                            latest_attempt_record is None
                            or latest_attempt_record.get("conclusion") != "success"
                        ):
                            reject_reason = "not from a successful latest workflow attempt"
                        elif len(matches) != 1:
                            reject_reason = "missing" if not matches else "ambiguous"
                        else:
                            artifact = matches[0]
                            if type(artifact.get("expired")) is not bool or artifact["expired"]:
                                reject_reason = "expired or has invalid expiration metadata"
                            elif (
                                type(artifact.get("size_in_bytes")) is not int
                                or artifact["size_in_bytes"] < 0
                                or artifact["size_in_bytes"] > MAX_EVIDENCE_ARTIFACT_BYTES
                            ):
                                raise TraceError(
                                    f"selected GitHub artifact {artifact_name} has invalid or oversized metadata"
                                )
                        if reject_reason is not None:
                            append_event(
                                trace, paths, kind="github_artifact_evidence_rejected",
                                stage=stage,
                                summary=f"Selected artifact {artifact_name} is {reject_reason}",
                                provenance="collector-observed", status=reject_status,
                                metadata=evidence_metadata,
                            )
                            observed += 1
                            continue

                        artifact = matches[0]
                        archive_bytes = gh_api_bytes(
                            f"/repos/{repo_owner}/{repo_name}/actions/artifacts/{artifact['id']}/zip"
                        )
                        evidence = parse_evidence_artifact(
                            archive_bytes, selection["archivePath"]
                        )
                        if evidence is None:
                            append_event(
                                trace, paths, kind="github_artifact_evidence_rejected",
                                stage=stage,
                                summary=(
                                    f"Selected artifact {artifact_name} does not contain "
                                    f"{selection['archivePath']}"
                                ),
                                provenance="collector-observed", status="unverified",
                                metadata=evidence_metadata,
                            )
                            observed += 1
                            continue
                        validate_evidence(evidence, stage=stage)
                        if evidence["evidenceType"] != selection["evidenceType"]:
                            rejection = "contains an unexpected evidence type"
                            status = "unverified"
                        elif evidence["sourceRevision"] != trace["targetRevision"]:
                            rejection = "contains evidence for a different revision"
                            status = "stale"
                        elif (
                            evidence["producerRun"]["runId"] != run_id
                            or evidence["producerRun"]["attempt"] != latest_attempt
                        ):
                            rejection = "evidence does not match the collected run attempt"
                            status = "unverified"
                        else:
                            rejection = None
                            status = "verified"
                        if rejection is not None:
                            append_event(
                                trace, paths, kind="github_artifact_evidence_rejected",
                                stage=stage,
                                summary=f"Selected artifact {artifact_name} {rejection}",
                                provenance="collector-observed", status=status,
                                metadata=evidence_metadata,
                            )
                            observed += 1
                            continue

                        evidence_metadata["artifact_id"] = str(artifact["id"])
                        evidence_metadata["evidence"] = evidence
                        artifact_url = artifact.get("url")
                        append_event(
                            trace, paths, kind="github_artifact_evidence_observed",
                            stage=stage,
                            summary=(
                                f"Validated {selection['evidenceType']} evidence "
                                f"from artifact {artifact_name}"
                            ),
                            provenance="provider-verified", status="verified",
                            metadata=evidence_metadata,
                            references=[{"type": "url", "value": safe_url(artifact_url)}]
                            if artifact_url else None,
                        )
                        observed += 1

        for review in effective_reviews(reviews):
            state = review.get("state", "unknown")
            review_revision = review.get("commit_id")
            review_status = (
                "verified" if state == "APPROVED" and review_revision == head
                else "failed" if state == "CHANGES_REQUESTED" and review_revision == head
                else "unverified"
            )
            review_url = review.get("html_url")
            user = review.get("user") or {}
            append_event(
                trace, paths, kind="github_review_observed", stage="review",
                summary=f"Effective review state: {state}",
                provenance="provider-verified",
                status=review_status,
                metadata={
                    "review_id": str(review.get("id", "")),
                    "reviewer": str(user.get("login") or user.get("id") or ""),
                    "state": state,
                    "sourceRevision": review_revision or "",
                    "headSha": head,
                    "evidenceType": "github-review",
                },
                references=[{"type": "url", "value": safe_url(review_url)}] if review_url else None,
            )
            observed += 1

        for deployment in deployments:
            deployment_id = str(deployment.get("id") or "")
            if not deployment_id or not deployment_id.isdecimal():
                raise TraceError("GitHub deployment is missing a valid numeric id")
            deployment_url = deployment.get("url")
            append_event(
                trace, paths, kind="github_deployment_observed", stage="deploy",
                summary=f"Deployment reference: {deployment.get('environment', 'unknown environment')}",
                provenance="provider-verified", status="unverified",
                metadata={
                    "deployment_id": deployment_id,
                    "deploymentEnvironment": deployment.get("environment", ""),
                    "sourceRevision": deployment.get("sha", ""),
                    "evidenceType": "github-deployment",
                },
                references=[{"type": "url", "value": safe_url(deployment_url)}] if deployment_url else None,
            )
            observed += 1
            deployment_status_pages = gh_api_json(
                f"/repos/{repo_owner}/{repo_name}/deployments/{deployment_id}/statuses",
                paginate=True,
            )
            deployment_statuses = github_api_items(deployment_status_pages)
            latest_terminal_status = next(
                (
                    status for status in deployment_statuses
                    if status.get("state") in {"success", "failure", "error"}
                ),
                None,
            )
            for deployment_status in deployment_statuses:
                state = deployment_status.get("state", "unknown")
                status_url = deployment_status.get("target_url") or deployment_status.get("url")
                append_event(
                    trace, paths, kind="github_deployment_status_observed", stage="deploy",
                    summary=f"Deployment status: {state}",
                    provenance="provider-verified",
                    status=github_observation_status(state),
                    metadata={
                        "deployment_id": deployment_id,
                        "deployment_status_id": str(deployment_status.get("id", "")),
                        "state": state,
                        "sourceRevision": deployment.get("sha", ""),
                        "evidenceType": "github-deployment-status",
                    },
                    references=[{"type": "url", "value": safe_url(status_url)}] if status_url else None,
                )
                observed += 1
                if deployment_status is latest_terminal_status:
                    deployed_revision = require_revision(
                        deployment.get("sha"), "GitHub deployment sha"
                    )
                    environment = require_text(
                        deployment.get("environment"), "GitHub deployment environment"
                    )
                    lineage_verified = github_deployment_lineage_verified(
                        f"{repo_owner}/{repo_name}",
                        trace["targetRevision"],
                        deployed_revision,
                    )
                    lineage_evidence = {
                        "schemaVersion": 1,
                        "evidenceType": "deployment-lineage",
                        "environment": environment,
                        "artifactId": deployment_id,
                        "sourceRevision": trace["targetRevision"],
                        "deployedRevision": deployed_revision,
                        "lineageVerified": lineage_verified,
                        "result": "succeeded" if state == "success" else "failed",
                    }
                    append_event(
                        trace, paths, kind="github_deployment_lineage_observed",
                        stage="deploy",
                        summary=(
                            f"Deployment lineage "
                            f"{'verified' if lineage_verified else 'unverified'}"
                        ),
                        provenance="provider-verified",
                        status=(
                            "verified"
                            if lineage_verified and state == "success"
                            else "failed"
                            if lineage_verified
                            else "unverified"
                        ),
                        metadata={
                            "producer": github_deployment_producer(
                                policy, f"{repo_owner}/{repo_name}", environment
                            ),
                            "evidence": lineage_evidence,
                        },
                        references=(
                            [{"type": "url", "value": safe_url(status_url)}]
                            if status_url else None
                        ),
                    )
                    observed += 1
        if not observed:
            append_event(
                trace, paths, kind="github_collection", stage="test",
                summary="GitHub API returned no policy-qualified workflow, review, or deployment evidence",
                provenance="provider-verified", status="unverified",
                metadata={"evidenceType": "collection-empty"},
            )
        print(f"Collected {observed} read-only GitHub evidence records.")
        return 0
    except (
        TraceError,
        IndexError,
        KeyError,
        TypeError,
        ValueError,
        OSError,
        subprocess.SubprocessError,
    ) as exc:
        append_event(
            trace, paths, kind="github_collection_error", stage="test",
            summary=f"GitHub evidence collection failed: {exc}",
            provenance="collector-observed", status="failed",
            metadata={"evidenceType": "collection-error"},
        )
        raise


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="subcommand", required=True)

    init = commands.add_parser("init", help="create a trace for an explicit change directory")
    init.add_argument("--repo")
    init.add_argument("--change-dir", required=True)
    init.add_argument("--output-dir", default=".fabric-traces")
    init.add_argument("--policy")
    init.add_argument("--predecessor")
    init.add_argument("--simulation", action="store_true")
    init.set_defaults(handler=lambda args: (initialize(args), 0)[1])

    record = commands.add_parser("record", help="record self-reported activity")
    record.add_argument("--trace-dir", required=True)
    record.add_argument("--kind", required=True)
    record.add_argument("--stage", choices=STAGES, required=True)
    record.add_argument("--summary", required=True)
    record.add_argument("--session-ref")
    record.add_argument("--url")
    record.add_argument("--metadata-json")
    record.set_defaults(handler=command_record)

    run = commands.add_parser("run", help="execute and record one local command")
    run.add_argument("--trace-dir", required=True)
    run.add_argument("--stage", choices=STAGES, required=True)
    run.add_argument("--summary")
    run.add_argument("command", nargs=argparse.REMAINDER)
    run.set_defaults(handler=command_run)

    collect = commands.add_parser("collect-github", help="collect read-only GitHub evidence")
    collect.add_argument("--trace-dir", required=True)
    collect.add_argument("--repo", required=True)
    collect.add_argument("--pr", required=True, type=int)
    collect.set_defaults(handler=command_collect_github)

    report = commands.add_parser("report", help="write JSON and Markdown reports")
    report.add_argument("--trace-dir", required=True)
    report.add_argument("--format", choices=("json", "markdown"), default="json")
    report.set_defaults(handler=command_report)

    check = commands.add_parser("check", help="exit nonzero unless the trace is verified complete")
    check.add_argument("--trace-dir", required=True)
    check.set_defaults(handler=command_check)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    try:
        args = build_parser().parse_args(argv)
        return int(args.handler(args))
    except TraceError as exc:
        print(f"fabric-trace: {exc}", file=sys.stderr)
        return 2
    except (
        IndexError,
        KeyError,
        TypeError,
        ValueError,
        OSError,
        subprocess.SubprocessError,
    ) as exc:
        print(f"fabric-trace: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
