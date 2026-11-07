#!/usr/bin/env python3
"""Report the advisory skill route without changing mode or repository controls."""

from __future__ import annotations

import argparse
import json


ACTIONS = {
    "propose": "propose",
    "explore": "explore",
    "new": "new-change",
    "continue": "continue-change",
    "ff": "ff-change",
    "apply": "apply-change",
    "update": "update-change",
    "verify": "verify-change",
    "sync": "sync-specs",
    "archive": "archive-change",
    "bulk-archive": "bulk-archive-change",
    "onboard": "onboard",
}


def route(action: str, mode: str = "fabric") -> dict[str, str]:
    if mode not in {"fabric", "standalone"}:
        raise ValueError(f"Unsupported work mode: {mode}")
    if action not in ACTIONS:
        raise ValueError(f"Unsupported action: {action}")
    prefix = "fabric" if mode == "fabric" else "openspec"
    return {
        "mode": mode,
        "skill": f"{prefix}-{ACTIONS[action]}",
        "repository_controls": "unchanged",
        "kind": "advisory",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--action", choices=ACTIONS, required=True)
    parser.add_argument("--mode", choices=("fabric", "standalone"), default="fabric",
                        help="Use standalone only when explicitly selected by the user.")
    arguments = parser.parse_args()
    print(json.dumps(route(arguments.action, arguments.mode)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
