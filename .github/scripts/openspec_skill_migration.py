"""Validate revision-bound, reviewed OpenSpec skill replacement plans."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

SUPPORTED_OPENSPEC_VERSION = "1.16.0"
MIGRATION_SCHEMA_VERSION = 1
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
Operation = tuple[str, Path, Path | None]


class MigrationValidationError(ValueError):
    """A migration lacks safe, content-bound replacement evidence."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise MigrationValidationError(message)


def _skill_path(value: object, prefix: str) -> Path:
    _require(isinstance(value, str), "skill path must be a string")
    parts = str(value).split("/")
    _require(
        len(parts) >= 4
        and parts[:2] == [".github", "skills"]
        and parts[2].startswith(prefix)
        and not any(part in ("", ".", "..") or "\\" in part or ":" in part for part in parts),
        f"invalid {prefix} skill path: {value!r}",
    )
    return Path(str(value))


def _safe_path(root: Path, relative: Path) -> Path:
    candidate = root / relative
    _require(
        candidate.resolve().is_relative_to(root.resolve())
        and not any(path.is_symlink() or getattr(path, "is_junction", lambda: False)()
                    for path in (candidate, *candidate.parents) if path != root.parent),
        f"linked or escaping migration path: {relative}",
    )
    return candidate


def _safe_file(root: Path, relative: Path) -> Path:
    candidate = _safe_path(root, relative)
    _require(candidate.is_file(), f"required migration file missing: {relative}")
    return candidate


def _verify_hash(path: Path, expected: object) -> None:
    _require(
        isinstance(expected, str) and SHA256_PATTERN.fullmatch(expected) is not None,
        f"invalid SHA-256 for {path.name}",
    )
    _require(
        hashlib.sha256(path.read_bytes()).hexdigest() == expected,
        f"reviewed content changed: {path}",
    )


def _validate_header(review: object, manifest: dict, target_version: str) -> dict:
    _require(isinstance(review, dict), "migration review must be an object")
    _require(type(review.get("schema_version")) is int
             and review["schema_version"] == MIGRATION_SCHEMA_VERSION,
             "unsupported migration schema")
    expected = {
        "repository": manifest["source"]["repository"],
        "from_version": manifest["source"]["version"],
        "to_version": target_version,
        "openspec_version": SUPPORTED_OPENSPEC_VERSION,
    }
    for field, value in expected.items():
        _require(review.get(field) == value, f"migration {field} mismatch")
    for field in ("reviewed_by", "review_reference"):
        _require(isinstance(review.get(field), str) and bool(review[field].strip()),
                 f"migration requires {field}")
    _require(isinstance(review.get("files"), list) and bool(review["files"]),
             "migration requires a nonempty files array")
    return review


def _entry_paths(entry: object) -> tuple[Path, Path, Path]:
    _require(isinstance(entry, dict), "migration file entry must be an object")
    retired = _skill_path(entry.get("path"), "openspec-")
    replacement = _skill_path(entry.get("replacement_path"), "openspec-")
    fabric = _skill_path(entry.get("fabric_path"), "fabric-")
    _require(fabric.name == "SKILL.md", "Fabric entry point must be SKILL.md")
    _require(len(fabric.parts) == 4, "Fabric entry point must be a skill root")
    return retired, replacement, fabric


def _verify_entry(
    entry: dict, roots: tuple[Path, Path, Path], operations: list[Operation],
    paths: tuple[Path, Path, Path],
) -> Path:
    old_root, upstream_root, destination_root = roots
    retired, replacement, fabric = paths
    old_file = _safe_file(old_root, retired)
    consumer_file = _safe_file(destination_root, retired)
    _verify_hash(old_file, entry.get("sha256"))
    _verify_hash(consumer_file, entry.get("sha256"))
    upstream_file = _safe_file(upstream_root, replacement)
    _verify_hash(upstream_file, entry.get("replacement_sha256"))
    _safe_file(upstream_root, replacement.parent / "SKILL.md")
    _safe_path(destination_root, fabric)
    fabric_source = next(
        (source for action, destination, source in operations
         if action == "copy" and destination == destination_root / fabric),
        destination_root / fabric,
    )
    _require(fabric_source is not None and fabric_source.is_file(),
             f"Fabric entry point unavailable: {fabric}")
    _require(not any(action == "delete" and destination == destination_root / fabric
                     for action, destination, _ in operations),
             f"Fabric entry point is being removed: {fabric}")
    _safe_file(fabric_source.parents[3], fabric)
    _verify_hash(fabric_source, entry.get("fabric_sha256"))
    return upstream_file


def _replacement_operation(
    destination_root: Path, retired: Path, replacement: Path, source: Path,
) -> list[Operation]:
    destination = _safe_path(destination_root, replacement)
    if replacement != retired and destination.exists():
        _safe_file(destination_root, replacement)
        _require(destination.read_bytes() == source.read_bytes(),
                 f"consumer-owned replacement collision: {replacement}")
    if replacement == retired:
        return [("copy", destination, source)]
    operations: list[Operation] = [("delete", destination_root / retired, None)]
    if not destination.exists():
        operations.append(("copy", destination, source))
    return operations


def plan_migration(
    review: object, manifest: dict, target_version: str,
    roots: tuple[Path, Path, Path], pending: set[Path],
    operations: list[Operation], protected: set[Path],
) -> list[Operation]:
    """Return operations only after validating every review entry."""
    review = _validate_header(review, manifest, target_version)
    migration_operations: list[Operation] = []
    retired_paths: set[Path] = set()
    replacement_paths: set[Path] = set()
    for entry in review["files"]:
        retired, replacement, fabric = _entry_paths(entry)
        _require(retired in pending and retired not in retired_paths,
                 f"path is not an unchanged migration candidate or is duplicate: {retired}")
        _require(not {retired, replacement} & protected, "protected migration path")
        _require(replacement not in replacement_paths, "duplicate replacement path")
        source = _verify_entry(entry, roots, operations, (retired, replacement, fabric))
        migration_operations.extend(
            _replacement_operation(roots[2], retired, replacement, source))
        retired_paths.add(retired)
        replacement_paths.add(replacement)
    _require(retired_paths == pending, "review must cover every retired OpenSpec file")
    for entry in review["files"]:
        retired, replacement, _ = _entry_paths(entry)
        _require(replacement not in retired_paths or replacement == retired,
                 "replacement overlaps another retired file")
    return migration_operations
