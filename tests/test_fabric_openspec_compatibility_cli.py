"""Exercise the supported OpenSpec CLI in an isolated project."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


class FabricOpenSpecCliTests(unittest.TestCase):
    def test_isolated_change_discovery_and_instructions(self) -> None:
        executable = shutil.which("openspec")
        self.assertIsNotNone(executable, "OpenSpec CLI is required for compatibility testing")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            environment = os.environ.copy()
            environment.update(
                {
                    "HOME": str(root),
                    "USERPROFILE": str(root),
                    "XDG_CONFIG_HOME": str(root / "config"),
                    "APPDATA": str(root / "appdata"),
                    "OPENSPEC_TELEMETRY": "0",
                    "CI": "1",
                }
            )

            def invoke(*args: str) -> str:
                result = subprocess.run(
                    [executable, *args],
                    cwd=root,
                    env=environment,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                return result.stdout

            self.assertEqual(invoke("--version").strip(), "1.16.0")
            invoke("init", "--tools", "none", "--no-copilot-cloud")
            context = json.loads(invoke("context", "--json"))
            self.assertEqual(Path(context["root"]["path"]).resolve(), root.resolve())
            invoke("new", "change", "compatibility-test")
            status = json.loads(invoke("status", "--change", "compatibility-test", "--json"))
            proposal = next(item for item in status["artifacts"] if item["id"] == "proposal")
            self.assertEqual(proposal["status"], "ready")
            instructions = json.loads(
                invoke("instructions", "proposal", "--change", "compatibility-test", "--json")
            )
            self.assertEqual(instructions["artifactId"], "proposal")
            self.assertTrue(instructions["template"])
            self.assertEqual(
                Path(instructions["resolvedOutputPath"]).resolve(),
                (root / "openspec" / "changes" / "compatibility-test" / "proposal.md").resolve(),
            )


if __name__ == "__main__":
    unittest.main()
