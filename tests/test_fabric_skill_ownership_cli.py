"""Verify upstream generation/update preserves the separately owned Fabric skills."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ["propose", "explore", "new", "continue", "apply", "update", "ff",
             "sync", "archive", "bulk-archive", "verify", "onboard"]


class FabricSkillOwnershipCliTests(unittest.TestCase):
    def test_upstream_refresh_is_exact_and_preserves_fabric_workflows(self) -> None:
        executable = shutil.which("openspec")
        self.assertIsNotNone(executable, "Supported OpenSpec CLI is required")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / "config" / "openspec"
            config.mkdir(parents=True)
            (config / "config.json").write_text(json.dumps({
                "profile": "custom", "workflows": WORKFLOWS, "delivery": "skills",
                "telemetry": {"enabled": False},
            }), encoding="utf-8")
            environment = os.environ.copy()
            environment.update({
                "XDG_CONFIG_HOME": str(root / "config"),
                "XDG_DATA_HOME": str(root / "data"),
                "OPENSPEC_TELEMETRY": "0", "CI": "1",
            })

            def invoke(*arguments: str) -> str:
                result = subprocess.run(
                    [executable, *arguments], cwd=root, env=environment,
                    capture_output=True, text=True, timeout=120, check=True,
                )
                return result.stdout

            self.assertEqual(invoke("--version").strip(), "1.16.0")
            invoke("init", "--tools", "github-copilot", "--profile", "custom",
                   "--no-copilot-cloud", "--no-animation")
            generated = root / ".github" / "skills"
            upstream = {}
            for path in generated.glob("openspec-*/SKILL.md"):
                relative = path.relative_to(generated)
                upstream[relative] = path.read_bytes()
                generated_parts = path.read_text(encoding="utf-8").split("---", 2)
                committed_parts = (ROOT / ".github" / "skills" / relative).read_text(
                    encoding="utf-8"
                ).split("---", 2)
                self.assertEqual(len(generated_parts), 3, path)
                self.assertEqual(len(committed_parts), 3, relative)
                generated_metadata = yaml.safe_load(generated_parts[1])
                committed_metadata = yaml.safe_load(committed_parts[1])
                # Upstream's legacy skill version is distinct from generatedBy.
                generated_metadata["metadata"].pop("version", None)
                committed_metadata["metadata"].pop("version", None)
                self.assertEqual(generated_metadata, committed_metadata, relative)
                self.assertEqual(generated_parts[0], committed_parts[0], relative)
                self.assertEqual(generated_parts[2], committed_parts[2], relative)
            self.assertEqual(len(upstream), len(WORKFLOWS))
            for path in (ROOT / ".github" / "skills").glob("fabric-*"):
                shutil.copytree(path, generated / path.name)
            fabric = {path.relative_to(generated): path.read_bytes()
                      for path in generated.glob("fabric-*/**/*") if path.is_file()}
            invoke("update", "--force")
            for relative, expected in upstream.items():
                self.assertEqual((generated / relative).read_bytes(), expected)
            for relative, expected in fabric.items():
                self.assertEqual((generated / relative).read_bytes(), expected)


if __name__ == "__main__":
    unittest.main()
