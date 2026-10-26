"""Contract checks for independent canonical-repository script CI."""

from pathlib import Path
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[2]


class SharedScriptWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.content = (ROOT / ".github" / "workflows" / "shared-script-tests.yml").read_text(
            encoding="utf-8"
        )
        self.workflow = yaml.safe_load(self.content)
        self.job = self.workflow["jobs"]["shared-script-tests"]

    def test_every_canonical_pull_request_is_covered(self) -> None:
        # PyYAML's YAML 1.1 loader treats the unquoted Actions "on" key as True.
        triggers = self.workflow[True]
        self.assertEqual(set(triggers), {"pull_request", "push", "workflow_dispatch"})
        self.assertIsNone(triggers["pull_request"])
        self.assertEqual(triggers["push"], {"branches": ["main"]})
        self.assertIsNone(triggers["workflow_dispatch"])
        self.assertEqual(self.job["if"], "github.repository == 'ralphke/agentic-shared'")
        self.assertEqual(self.workflow["permissions"], {"contents": "read"})
        self.assertNotIn("permissions", self.job)
        self.assertEqual(self.workflow["env"]["PYTHONDONTWRITEBYTECODE"], "1")

    def test_full_discovery_has_dependencies_and_propagates_failures(self) -> None:
        steps = self.job["steps"]
        self.assertEqual(steps[0]["uses"], "actions/checkout@v7")
        self.assertEqual(steps[1]["uses"], "actions/setup-python@v6")
        self.assertEqual(steps[1]["with"]["python-version"], "3.14")
        self.assertEqual(
            steps[2]["run"], "python -m pip install --disable-pip-version-check PyYAML"
        )
        self.assertEqual(
            steps[3]["run"], 'python -m unittest discover -s .github/scripts -p "test_*.py"'
        )
        self.assertEqual(len(steps), 4)
        self.assertNotIn("continue-on-error", self.job)
        for step in steps:
            self.assertNotIn("continue-on-error", step)
            self.assertNotIn("if", step)
        self.assertNotIn("secrets.", self.content)

    def test_ci_does_not_restore_missing_committed_policy(self) -> None:
        self.assertNotIn("restore_openspec_contracts.py", self.content)
        self.assertNotIn("openspec update", self.content)
        self.assertNotIn("pull_request_target", self.content)
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("skips consumer repositories", readme)


if __name__ == "__main__":
    unittest.main()
