#!/usr/bin/env python3
"""Check the Software Fabric OpenSpec and Node.js compatibility baseline."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


CONFIG = Path(__file__).with_name("openspec-compatibility.json")
NODE_VERSION = re.compile(r"^v?(\d+)\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")


class CompatibilityError(ValueError):
    """The integration cannot run with the detected versions."""


def check_versions(node_version: str, openspec_version: str, config: dict) -> None:
    supported = config.get("supportedOpenSpecVersions")
    minimum_node = config.get("minimumNodeMajor")
    if (
        not isinstance(supported, list)
        or not supported
        or not all(isinstance(version, str) and version for version in supported)
        or type(minimum_node) is not int
        or minimum_node < 1
    ):
        raise CompatibilityError("invalid Fabric compatibility configuration")

    match = NODE_VERSION.fullmatch(node_version.strip())
    if match is None:
        raise CompatibilityError(f"unrecognized Node.js version: {node_version!r}")
    if int(match.group(1)) < minimum_node:
        raise CompatibilityError(
            f"unsupported Node.js version {node_version}; "
            f"Fabric requires Node.js {minimum_node} or later"
        )
    if openspec_version.strip() not in supported:
        raise CompatibilityError(
            f"unsupported OpenSpec version {openspec_version}; "
            f"Fabric supports: {', '.join(supported)}"
        )


def read_version(command: str) -> str:
    executable = shutil.which(command)
    if executable is None:
        raise CompatibilityError(f"cannot run {command} --version: command not found")
    try:
        result = subprocess.run(
            [executable, "--version"], check=True, capture_output=True, text=True
        )
    except OSError as error:
        raise CompatibilityError(f"cannot run {command} --version: {error}") from error
    except subprocess.CalledProcessError as error:
        detail = error.stderr.strip() or error.stdout.strip()
        raise CompatibilityError(
            f"{command} --version failed with exit code {error.returncode}: {detail}"
        ) from error
    return result.stdout.strip()


def main() -> int:
    try:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        if not isinstance(config, dict):
            raise CompatibilityError("invalid Fabric compatibility configuration")
        node_version = read_version("node")
        openspec_version = read_version("openspec")
        check_versions(node_version, openspec_version, config)
    except (OSError, UnicodeError, json.JSONDecodeError, CompatibilityError) as error:
        print(f"Fabric compatibility check failed: {error}", file=sys.stderr)
        return 1
    print(f"Fabric compatibility verified: Node.js {node_version}, OpenSpec {openspec_version}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
