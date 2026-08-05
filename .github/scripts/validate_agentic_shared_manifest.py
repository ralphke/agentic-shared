#!/usr/bin/env python3
"""Validate a consumer repository's .agentic-shared.yml manifest."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import yaml

SUPPORTED_ASSET_GROUPS = {
    "agents",
    "skills",
    "prompts",
    "instructions",
    "workflows",
    "issue_templates",
    "specs",
}
SUPPORTED_OWNERSHIP_MODES = {"managed", "extended", "local"}
VERSION_PATTERN = re.compile(r"^v\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
REPOSITORY_PATTERN = re.compile(r"^[^/\s]+/[^/\s]+$")


class ManifestValidationError(ValueError):
    """Raised when a manifest violates the consumer sync contract."""


def _require_mapping(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ManifestValidationError(f"{name} must be a YAML mapping")
    return value


def validate_manifest(manifest: Any) -> dict[str, Any]:
    """Return a valid manifest or raise ManifestValidationError."""
    manifest = _require_mapping(manifest, "manifest")
    source = _require_mapping(manifest.get("source"), "source")

    repository = source.get("repository")
    if not isinstance(repository, str) or not REPOSITORY_PATTERN.fullmatch(repository):
        raise ManifestValidationError(
            "source.repository must use the owner/name format"
        )

    version = source.get("version")
    if not isinstance(version, str) or not VERSION_PATTERN.fullmatch(version):
        raise ManifestValidationError(
            "source.version must be a semver tag such as v1.0.0"
        )

    assets = _require_mapping(manifest.get("assets"), "assets")
    if not assets:
        raise ManifestValidationError("assets must contain at least one asset group")

    unknown_groups = set(assets) - SUPPORTED_ASSET_GROUPS
    if unknown_groups:
        groups = ", ".join(sorted(unknown_groups))
        raise ManifestValidationError(f"unsupported asset group(s): {groups}")

    for asset_group, ownership_mode in assets.items():
        if ownership_mode not in SUPPORTED_OWNERSHIP_MODES:
            modes = ", ".join(sorted(SUPPORTED_OWNERSHIP_MODES))
            raise ManifestValidationError(
                f"assets.{asset_group} must be one of: {modes}"
            )

    protected_paths = manifest.get("protected_paths", [])
    if not isinstance(protected_paths, list) or not all(
        isinstance(path, str) for path in protected_paths
    ):
        raise ManifestValidationError("protected_paths must be an array of strings")

    if len(set(protected_paths)) != len(protected_paths):
        raise ManifestValidationError("protected_paths must not contain duplicates")

    for path in protected_paths:
        normalized = path.replace("\\", "/")
        if (
            not normalized
            or normalized.startswith("/")
            or re.match(r"^[A-Za-z]:/", normalized)
        ):
            raise ManifestValidationError(f"protected path must be relative: {path!r}")
        if ".." in normalized.split("/"):
            raise ManifestValidationError(
                f"protected path must not traverse parents: {path!r}"
            )

    return manifest


def main() -> int:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else ".agentic-shared.yml")
    try:
        with path.open(encoding="utf-8") as manifest_file:
            manifest = yaml.safe_load(manifest_file)
        validate_manifest(manifest)
    except FileNotFoundError:
        print(f"Manifest not found: {path}", file=sys.stderr)
        return 1
    except yaml.YAMLError as error:
        print(f"Manifest YAML is invalid: {error}", file=sys.stderr)
        return 1
    except ManifestValidationError as error:
        print(f"Manifest invalid: {error}", file=sys.stderr)
        return 1

    print(f"Manifest valid: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
