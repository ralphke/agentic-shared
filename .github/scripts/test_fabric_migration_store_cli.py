"""Verify consumer-local defaults and explicit stores using OpenSpec 1.16.0."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


class FabricMigrationStoreCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.executable = shutil.which("openspec")
        if self.executable is None:
            self.skipTest("OpenSpec 1.16.0 required; run in compatibility environment")
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.consumer = self.root / "consumer"
        self.consumer.mkdir()
        self.environment = os.environ.copy()
        self.environment.update({
            "HOME": str(self.root), "USERPROFILE": str(self.root),
            "XDG_CONFIG_HOME": str(self.root / "config"),
            "XDG_DATA_HOME": str(self.root / "data"),
            "LOCALAPPDATA": str(self.root / "localappdata"),
            "APPDATA": str(self.root / "appdata"),
            "OPENSPEC_TELEMETRY": "0", "CI": "1",
        })

    def invoke(self, *arguments: str) -> str:
        result = subprocess.run(
            [self.executable, *arguments], cwd=self.consumer, env=self.environment,
            capture_output=True, text=True, check=True, timeout=60,
        )
        return result.stdout

    def test_local_default_and_explicit_shared_selection(self) -> None:
        self.assertEqual(self.invoke("--version").strip(), "1.16.0")
        self.invoke("init", "--tools", "none", "--no-copilot-cloud")
        shared = self.root / "shared"
        self.invoke("store", "setup", "migration-shared", "--path", str(shared),
                    "--no-init-git", "--json")
        local_context = json.loads(self.invoke("context", "--json"))
        shared_context = json.loads(self.invoke(
            "context", "--json", "--store", "migration-shared"))
        self.assertEqual(Path(local_context["root"]["path"]).resolve(),
                         self.consumer.resolve())
        self.assertEqual(Path(shared_context["root"]["path"]).resolve(), shared.resolve())
        self.invoke("new", "change", "consumer-product")
        self.assertTrue((self.consumer / "openspec/changes/consumer-product").is_dir())
        self.assertFalse((shared / "openspec/changes/consumer-product").exists())
        self.invoke("new", "change", "shared-work", "--store", "migration-shared")
        self.assertTrue((shared / "openspec/changes/shared-work").is_dir())
        self.assertFalse((self.consumer / "openspec/changes/shared-work").exists())
        context_after = json.loads(self.invoke("context", "--json"))
        self.assertEqual(Path(context_after["root"]["path"]).resolve(),
                         self.consumer.resolve())


if __name__ == "__main__":
    unittest.main()
