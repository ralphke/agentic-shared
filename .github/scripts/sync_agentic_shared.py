#!/usr/bin/env python3
"""Synchronize declared shared assets while preserving consumer extensions."""

from __future__ import annotations

import argparse
import fnmatch
import json
import shutil
import sys
from collections.abc import Iterable
from pathlib import Path

import yaml
from openspec_skill_migration import MigrationValidationError, plan_migration
from validate_agentic_shared_manifest import (
    ManifestValidationError,
    validate_manifest,
)

ASSET_ROOTS = {
    "agents": Path(".github/agents"),
    "skills": Path(".github/skills"),
    "prompts": Path(".github/prompts"),
    "instructions": Path(".github/instructions"),
    "workflows": Path(".github/workflows"),
    "issue_templates": Path(".github/ISSUE_TEMPLATE"),
    "specs": Path("openspec"),
}


class SyncConflictError(RuntimeError):
    """Raised when a managed consumer file cannot be updated safely."""


def _is_protected(path: Path, protected_patterns: Iterable[str]) -> bool:
    normalized = path.as_posix()
    return any(fnmatch.fnmatch(normalized, pattern) for pattern in protected_patterns)


def _relative_files(root: Path, asset_root: Path) -> set[Path]:
    directory = root / asset_root
    if not directory.exists():
        return set()
    return {
        path.relative_to(root)
        for path in directory.rglob("*")
        if path.is_file()
    }


def _same_file(left: Path, right: Path) -> bool:
    return left.exists() and right.exists() and left.read_bytes() == right.read_bytes()


def _is_openspec_skill(path: Path) -> bool:
    parts = path.parts
    return (
        len(parts) >= 4
        and parts[:2] == (".github", "skills")
        and parts[2].startswith("openspec-")
    )


def _new_upstream_collisions(
    manifest: dict, old_root: Path, new_root: Path, destination_root: Path,
) -> list[Path]:
    if manifest["assets"].get("skills", "local") == "local":
        return []
    return [
        path for path in sorted(_relative_files(new_root, ASSET_ROOTS["skills"]))
        if _is_openspec_skill(path)
        and not _is_protected(path, manifest.get("protected_paths", []))
        and not (old_root / path).exists()
        and (destination_root / path).exists()
        and not _same_file(destination_root / path, new_root / path)
    ]


def synchronize(
    manifest: dict,
    old_root: Path,
    new_root: Path,
    destination_root: Path,
    target_version: str,
    migration_review: dict | None = None,
    upstream_root: Path | None = None,
) -> list[Path]:
    """Apply a three-way sync and return changed destination paths."""
    protected_patterns = manifest.get("protected_paths", [])
    conflicts: list[Path] = []
    migration_conflicts = _new_upstream_collisions(
        manifest, old_root, new_root, destination_root)
    operations: list[tuple[str, Path, Path | None]] = []

    for asset_group, ownership_mode in manifest["assets"].items():
        if ownership_mode == "local":
            continue

        asset_root = ASSET_ROOTS[asset_group]
        candidate_paths = (
            _relative_files(old_root, asset_root)
            | {path for path in _relative_files(new_root, asset_root)
               if not _is_openspec_skill(path)}
        )

        for relative_path in sorted(candidate_paths):
            if _is_protected(relative_path, protected_patterns):
                continue

            old_path = old_root / relative_path
            new_path = new_root / relative_path
            destination_path = destination_root / relative_path
            old_exists = old_path.exists()
            new_exists = new_path.exists() and not _is_openspec_skill(relative_path)
            destination_exists = destination_path.exists()

            if _is_openspec_skill(relative_path) and destination_exists and old_exists:
                migration_conflicts.append(relative_path)
                continue

            if not old_exists:
                if new_exists and (
                    not destination_exists or not _same_file(destination_path, new_path)
                ):
                    operations.append(("copy", destination_path, new_path))
                continue

            if old_exists and not destination_exists:
                if new_exists:
                    operations.append(("copy", destination_path, new_path))
                continue

            if old_exists and destination_exists and not _same_file(destination_path, old_path):
                if new_exists and not _same_file(new_path, old_path):
                    conflicts.append(relative_path)
                continue

            if not new_exists:
                if destination_exists:
                    operations.append(("delete", destination_path, None))
                continue

            if destination_exists and _same_file(destination_path, new_path):
                continue

            operations.append(("copy", destination_path, new_path))

    if migration_review is not None:
        try:
            if upstream_root is None:
                raise MigrationValidationError("migration requires an upstream source")
            review_paths = {
                path for root in (old_root, upstream_root, destination_root)
                for path in _relative_files(root, ASSET_ROOTS["skills"])
                if _is_protected(path, protected_patterns)
            }
            operations.extend(plan_migration(
                migration_review, manifest, target_version,
                (old_root, upstream_root, destination_root), set(migration_conflicts),
                operations, review_paths,
            ))
            migration_conflicts.clear()
        except MigrationValidationError as error:
            raise SyncConflictError(f"no files were changed: {error}") from error
    elif upstream_root is not None:
        raise SyncConflictError("no files were changed: upstream source requires migration review")

    if conflicts or migration_conflicts:
        messages = []
        if conflicts:
            paths = "\n".join(f"- {path.as_posix()}" for path in conflicts)
            messages.append("managed synchronization conflicts:\n" + paths)
        if migration_conflicts:
            paths = "\n".join(f"- {path.as_posix()}" for path in migration_conflicts)
            messages.append("OpenSpec skill paths require reviewed migration:\n" + paths)
        raise SyncConflictError("no files were changed:\n" + "\n".join(messages))

    changed_paths: list[Path] = []
    for operation, destination_path, source_path in operations:
        if operation == "delete":
            destination_path.unlink()
        else:
            if source_path is None:
                raise RuntimeError("copy operation is missing its source path")
            destination_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, destination_path)
        changed_paths.append(destination_path.relative_to(destination_root))

    manifest["source"]["version"] = target_version
    return changed_paths


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path(".agentic-shared.yml"))
    parser.add_argument("--old-source", type=Path, required=True)
    parser.add_argument("--new-source", type=Path, required=True)
    parser.add_argument("--destination", type=Path, default=Path("."))
    parser.add_argument("--target-version", required=True)
    parser.add_argument("--openspec-migration", type=Path)
    parser.add_argument("--upstream-source", type=Path)
    args = parser.parse_args()

    try:
        with args.manifest.open(encoding="utf-8") as manifest_file:
            manifest = yaml.safe_load(manifest_file)
        validate_manifest(manifest)
        migration_review = None
        if args.openspec_migration is not None:
            with args.openspec_migration.open(encoding="utf-8") as review_file:
                migration_review = json.load(review_file)
            if migration_review is None:
                raise SyncConflictError("migration review must be an object")
        changed_paths = synchronize(
            manifest,
            args.old_source,
            args.new_source,
            args.destination,
            args.target_version,
            migration_review,
            args.upstream_source,
        )
        with args.manifest.open("w", encoding="utf-8", newline="\n") as manifest_file:
            yaml.safe_dump(manifest, manifest_file, sort_keys=False)
    except FileNotFoundError as error:
        print(f"Required path not found: {error.filename}", file=sys.stderr)
        return 1
    except (ManifestValidationError, SyncConflictError, ValueError, yaml.YAMLError) as error:
        print(f"Sync failed: {error}", file=sys.stderr)
        return 1

    print(f"Synchronized {len(changed_paths)} path(s) to {args.target_version}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
