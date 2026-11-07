"""Distributed runtime and actual lifecycle workflow contracts."""

import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ".github/skills/fabric-verify-change/scripts"


class GateWorkflowTests(unittest.TestCase):
    def workflow(self, lifecycle):
        path = ROOT / f".github/workflows/fabric-{lifecycle}-gate.yml"
        return yaml.safe_load(path.read_text(encoding="utf-8"))

    def test_all_runtime_assets_are_in_distributed_skills_group(self):
        for filename in ("fabric_gate.py", "collect_fabric_evidence.py",
                         "run_fabric_gate_control.py", "gate-policy.json",
                         "gate-evidence.schema.json", "fabric_mapping.py", "fabric_control_policy.py"):
            with self.subTest(filename=filename):
                self.assertTrue((ROOT / RUNTIME / filename).is_file())
                self.assertFalse((ROOT / ".github/scripts" / filename).exists())

    def test_protected_default_checkout_never_uses_evaluated_code(self):
        for lifecycle in ("merge", "release", "archive"):
            workflow = self.workflow(lifecycle)
            job = next(iter(workflow["jobs"].values()))
            checkout = job["steps"][0]
            self.assertEqual(checkout["with"]["ref"],
                             "${{ github.event.repository.default_branch }}")
            self.assertFalse(checkout["with"]["persist-credentials"])
            self.assertIn("default_branch", job["if"])
            self.assertEqual(job["timeout-minutes"], 5)
            self.assertIn(RUNTIME, job["steps"][1]["run"])
            self.assertNotIn("${{", job["steps"][1]["run"])

    def test_merge_uses_target_event_and_minimal_write_permission(self):
        workflow = self.workflow("merge")
        events = workflow.get("on", workflow.get(True))
        self.assertIn("pull_request_target", events)
        self.assertNotIn("pull_request", events)
        self.assertEqual(workflow["permissions"]["contents"], "read")
        self.assertNotIn("statuses", workflow["permissions"])
        self.assertIn("request-merge", events["workflow_dispatch"]["inputs"]["operation"]["options"])
        self.assertEqual(workflow["jobs"]["merge-gate"]["environment"], "fabric-gate-control")
        self.assertEqual(workflow["jobs"]["merge-gate"]["steps"][1]["env"]["GH_TOKEN"],
                         "${{ secrets.FABRIC_GATE_APP_TOKEN }}")
        self.assertEqual(workflow["env"]["PYTHONDONTWRITEBYTECODE"], "1")

    def test_release_is_gated_publication_not_post_release_notification(self):
        workflow = self.workflow("release")
        events = workflow.get("on", workflow.get(True))
        self.assertEqual(set(events), {"workflow_dispatch"})
        job = workflow["jobs"]["release-gate"]
        self.assertEqual(job["environment"], "fabric-gate-control")
        self.assertEqual(workflow["permissions"]["contents"], "read")
        self.assertIn("--mode release", job["steps"][1]["run"])

    def test_archive_is_read_only_and_requires_deployed_revision(self):
        workflow = self.workflow("archive")
        self.assertTrue(all(value == "read" for value in workflow["permissions"].values()))
        job = workflow["jobs"]["archive-gate"]
        self.assertIn("--deployed-revision", job["steps"][1]["run"])
        self.assertIn("--change", job["steps"][1]["run"])
        self.assertNotIn("openspec archive", job["steps"][1]["run"])

    def test_non_dispatch_events_only_invalidate_never_request_merge(self):
        workflow = self.workflow("merge")
        command = workflow["jobs"]["merge-gate"]["steps"][1]["run"]
        non_dispatch = command.rsplit("else", 1)[1]
        self.assertIn("--mode invalidate", non_dispatch)
        self.assertNotIn("--execute-merge", non_dispatch)
        events = workflow.get("on", workflow.get(True))
        self.assertIn("schedule", events)
        self.assertIn("repository_dispatch", events)

    def test_documented_required_checks_are_actually_published(self):
        document = (ROOT / "doc/fabric-gate-evidence.md").read_text(encoding="utf-8")
        control = (ROOT / RUNTIME / "run_fabric_gate_control.py").read_text(encoding="utf-8")
        for name in ("Fabric / merge", "Fabric / release"):
            self.assertIn(f"**{name}**", document)
            self.assertIn(f'"{name}"', control)
        self.assertIn("start_check", control)
        self.assertNotIn("/statuses/", control)
        self.assertIn("preflight", document)
        self.assertIn("explicit", document)
        self.assertIn("does not constitute security approval", document)


if __name__ == "__main__":
    unittest.main()
