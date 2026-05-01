import json
import tempfile
import unittest
from pathlib import Path

from scripts.goal1171_clean_source_rtx_pod_preflight import run_preflight


class Goal1171CleanSourceRtxPodPreflightTest(unittest.TestCase):
    def test_dry_run_accepts_manifest_and_runner_shape(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            manifest = tmp_path / "manifest.json"
            runner = tmp_path / "runner.sh"
            manifest.write_text(json.dumps({"rows": [{} for _ in range(8)]}), encoding="utf-8")
            runner.write_text(
                "echo 'Refusing claim-grade run: git working tree is dirty.'\n",
                encoding="utf-8",
            )

            payload = run_preflight(dry_run=True, manifest_path=manifest, runner_path=runner)

        self.assertTrue(payload["valid"])
        self.assertEqual(payload["blockers"], [])
        self.assertTrue(payload["checks"]["manifest_has_eight_rows"])
        self.assertTrue(payload["checks"]["runner_refuses_dirty_tree"])

    def test_missing_manifest_is_blocker_even_in_dry_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            runner = tmp_path / "runner.sh"
            runner.write_text(
                "echo 'Refusing claim-grade run: git working tree is dirty.'\n",
                encoding="utf-8",
            )

            payload = run_preflight(
                dry_run=True,
                manifest_path=tmp_path / "missing.json",
                runner_path=runner,
            )

        self.assertFalse(payload["valid"])
        self.assertIn("manifest_exists", payload["blockers"])

    def test_runner_dirty_refusal_is_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            manifest = tmp_path / "manifest.json"
            runner = tmp_path / "runner.sh"
            manifest.write_text(json.dumps({"rows": [{} for _ in range(8)]}), encoding="utf-8")
            runner.write_text("echo unsafe\n", encoding="utf-8")

            payload = run_preflight(dry_run=True, manifest_path=manifest, runner_path=runner)

        self.assertFalse(payload["valid"])
        self.assertIn("runner_refuses_dirty_tree", payload["blockers"])


if __name__ == "__main__":
    unittest.main()
